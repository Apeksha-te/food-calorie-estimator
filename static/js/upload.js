// ============================================================
// upload.js – Food Upload & Prediction Logic
// ============================================================

let selectedFile   = null;
let lastResult     = null;
let webcamStream   = null;

// ---- Drag & Drop ----
const dropZone = document.getElementById('dropZone');
if (dropZone) {
  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) loadPreview(file);
  });
}

// ---- File input ----
function handleFileSelect(input) {
  const file = input.files[0];
  if (file) loadPreview(file);
}

function loadPreview(file) {
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    document.getElementById('previewImg').src = e.target.result;
    document.getElementById('dropContent').classList.add('d-none');
    document.getElementById('previewWrapper').classList.remove('d-none');
    document.getElementById('analyseBtn').disabled = false;
  };
  reader.readAsDataURL(file);
}

function removeImage(event) {
  event.stopPropagation();
  selectedFile = null;
  document.getElementById('fileInput').value = '';
  document.getElementById('previewImg').src = '';
  document.getElementById('previewWrapper').classList.add('d-none');
  document.getElementById('dropContent').classList.remove('d-none');
  document.getElementById('analyseBtn').disabled = true;
  hideResults();
}

// ---- Webcam ----
function startWebcam() {
  const container = document.getElementById('webcamContainer');
  container.classList.remove('d-none');
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      webcamStream = stream;
      document.getElementById('webcamVideo').srcObject = stream;
    })
    .catch(() => alert('Camera not available or permission denied.'));
}

function captureWebcam() {
  const video  = document.getElementById('webcamVideo');
  const canvas = document.createElement('canvas');
  canvas.width  = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  canvas.toBlob(blob => {
    const file = new File([blob], 'webcam_capture.jpg', { type: 'image/jpeg' });
    loadPreview(file);
    // Stop webcam
    webcamStream?.getTracks().forEach(t => t.stop());
    document.getElementById('webcamContainer').classList.add('d-none');
  }, 'image/jpeg');
}

// ---- Analyse Food ----
async function analyseFood() {
  if (!selectedFile) return;

  showLoader(true);
  hideResults();
  clearError();

  const formData = new FormData();
  formData.append('image', selectedFile);

  try {
    const response = await fetch('/predict', { method: 'POST', body: formData });
    const data = await response.json();

    if (!response.ok || data.error) {
      showError(data.error || 'Prediction failed. Please try another image.');
      return;
    }

    lastResult = data;
    displayResults(data);
  } catch (err) {
    showError('Network error. Please make sure the Flask server is running.');
  } finally {
    showLoader(false);
  }
}

// ---- Display Results ----
function displayResults(d) {
  // Food name & health label
  document.getElementById('rFoodName').textContent   = d.food_name;
  document.getElementById('rHealthLabel').textContent = d.health_label;
  document.getElementById('rHealthTip').textContent   = d.health_tip;

  // Nutrition
  document.getElementById('rCalories').textContent = d.calories;
  document.getElementById('rProtein').textContent  = d.protein;
  document.getElementById('rCarbs').textContent    = d.carbs;
  document.getElementById('rFat').textContent      = d.fat;

  // Confidence ring animation
  const circumference = 2 * Math.PI * 40; // r=40
  const conf = Math.min(d.confidence, 100);
  const dash = (conf / 100) * circumference;
  document.getElementById('rConfidence').textContent  = conf;
  document.getElementById('confCircle').setAttribute('stroke-dasharray', `${dash} ${circumference - dash}`);

  // Macro percentage bars
  const total = d.protein * 4 + d.carbs * 4 + d.fat * 9;  // calories from macros
  const pp = total > 0 ? ((d.protein * 4 / total) * 100).toFixed(0) : 0;
  const cp = total > 0 ? ((d.carbs  * 4 / total) * 100).toFixed(0) : 0;
  const fp = total > 0 ? ((d.fat    * 9 / total) * 100).toFixed(0) : 0;
  document.getElementById('proteinBar').style.width = pp + '%';
  document.getElementById('carbsBar').style.width   = cp + '%';
  document.getElementById('fatBar').style.width     = fp + '%';
  document.getElementById('proteinPct').textContent = pp + '%';
  document.getElementById('carbsPct').textContent   = cp + '%';
  document.getElementById('fatPct').textContent     = fp + '%';

  // Show result card, hide empty state
  document.getElementById('emptyState').classList.add('d-none');
  document.getElementById('resultCard').classList.remove('d-none');

  // Scroll to result on mobile
  if (window.innerWidth < 992) {
    document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// ---- Voice Output ----
function speakResult() {
  if (!lastResult) return;
  const d = lastResult;
  const text = `You ate ${d.food_name}. Calories: ${d.calories} kilocalories. Protein: ${d.protein} grams. Carbohydrates: ${d.carbs} grams. Fat: ${d.fat} grams. Confidence: ${d.confidence} percent. ${d.health_tip}`;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate  = 0.9;
  utter.pitch = 1;
  window.speechSynthesis.speak(utter);
}

// ---- PDF Download ----
function downloadPDF() {
  if (!lastResult) return;
  // Build a simple printable HTML and trigger browser print
  const d = lastResult;
  const html = `
    <html><head><title>CalorieAI Report</title>
    <style>
      body{font-family:Arial,sans-serif;padding:40px;color:#1a1a2e;}
      h1{color:#ff6b35;} table{width:100%;border-collapse:collapse;margin-top:20px;}
      td,th{padding:10px 14px;border:1px solid #ddd;text-align:left;}
      th{background:#ff6b35;color:white;}
      .tip{margin-top:20px;padding:14px;background:#fff3ee;border-left:4px solid #ff6b35;border-radius:4px;}
      .footer{margin-top:40px;color:#999;font-size:12px;}
    </style></head><body>
    <h1>🍽️ CalorieAI — Nutrition Report</h1>
    <p>Generated: ${new Date().toLocaleString()}</p>
    <table>
      <tr><th>Parameter</th><th>Value</th></tr>
      <tr><td>Food Name</td><td><strong>${d.food_name}</strong></td></tr>
      <tr><td>Calories</td><td>${d.calories} kcal</td></tr>
      <tr><td>Protein</td><td>${d.protein} g</td></tr>
      <tr><td>Carbohydrates</td><td>${d.carbs} g</td></tr>
      <tr><td>Fat</td><td>${d.fat} g</td></tr>
      <tr><td>Confidence</td><td>${d.confidence}%</td></tr>
      <tr><td>Health Label</td><td>${d.health_label}</td></tr>
    </table>
    <div class="tip"><strong>Health Tip:</strong> ${d.health_tip}</div>
    <div class="footer">AI-Based Food Calorie Estimator · Final Year Mini Project</div>
    </body></html>
  `;
  const win = window.open('', '_blank');
  win.document.write(html);
  win.document.close();
  win.print();
}

// ---- Reset ----
function resetForm() {
  removeImage({ stopPropagation: () => {} });
  hideResults();
  clearError();
}

// ---- Helpers ----
function showLoader(show) {
  const loader = document.getElementById('loader');
  const btn    = document.getElementById('analyseBtn');
  if (show) {
    loader.classList.remove('d-none');
    btn.disabled  = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analysing…';
  } else {
    loader.classList.add('d-none');
    btn.disabled  = false;
    btn.innerHTML = '<i class="fas fa-search me-2"></i>Analyse Nutrition';
  }
}

function hideResults() {
  document.getElementById('emptyState').classList.remove('d-none');
  document.getElementById('resultCard').classList.add('d-none');
}

function showError(msg) {
  const el = document.getElementById('errorMsg');
  el.textContent = msg;
  el.classList.remove('d-none');
}

function clearError() {
  const el = document.getElementById('errorMsg');
  el.textContent = '';
  el.classList.add('d-none');
}

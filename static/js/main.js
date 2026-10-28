// ============================================================
// main.js – Global JavaScript (theme toggle, particles)
// ============================================================

// ---- Theme Toggle ----
function toggleTheme() {
  const body = document.body;
  const btn  = document.querySelector('.theme-btn i');
  if (body.classList.contains('dark-theme')) {
    body.classList.replace('dark-theme', 'light-theme');
    if (btn) btn.className = 'fas fa-sun';
    localStorage.setItem('theme', 'light');
  } else {
    body.classList.replace('light-theme', 'dark-theme');
    if (btn) btn.className = 'fas fa-moon';
    localStorage.setItem('theme', 'dark');
  }
}

// Apply saved theme on load
(function applySavedTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.body.className = saved + '-theme';
  const btn = document.querySelector('.theme-btn i');
  if (btn) btn.className = saved === 'light' ? 'fas fa-sun' : 'fas fa-moon';
})();

// ---- Particle generator (hero page) ----
function spawnParticles() {
  const container = document.getElementById('particles');
  if (!container) return;
  for (let i = 0; i < 30; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.cssText = `
      left:${Math.random()*100}%;
      animation-duration:${6 + Math.random()*12}s;
      animation-delay:${Math.random()*8}s;
      width:${2+Math.random()*4}px;
      height:${2+Math.random()*4}px;
      opacity:${0.1+Math.random()*0.3};
    `;
    container.appendChild(p);
  }
}
document.addEventListener('DOMContentLoaded', spawnParticles);

// ---- BMI Calculator (shared across upload page) ----
function calculateBMI() {
  const h = parseFloat(document.getElementById('bmiHeight')?.value);
  const w = parseFloat(document.getElementById('bmiWeight')?.value);
  const a = parseFloat(document.getElementById('bmiAge')?.value);
  const el = document.getElementById('bmiResult');
  if (!el) return;
  if (!h || !w || h <= 0 || w <= 0) {
    el.innerHTML = '<span class="text-danger">Please enter valid height and weight.</span>';
    el.classList.remove('d-none');
    return;
  }
  const hm  = h / 100;
  const bmi = (w / (hm * hm)).toFixed(1);
  let category, color, advice;
  if      (bmi < 18.5) { category = 'Underweight'; color = '#3498db'; advice = 'Increase caloric intake with nutrient-dense foods.'; }
  else if (bmi < 25)   { category = 'Normal';      color = '#2ecc71'; advice = 'Great! Maintain your healthy lifestyle.'; }
  else if (bmi < 30)   { category = 'Overweight';  color = '#f39c12'; advice = 'Consider more physical activity and balanced meals.'; }
  else                 { category = 'Obese';        color = '#e74c3c'; advice = 'Consult a doctor and start a structured diet plan.'; }

  el.innerHTML = `
    <div class="d-flex align-items-center gap-3 flex-wrap">
      <div>
        <div class="fw-bold fs-5" style="color:${color}">BMI: ${bmi}</div>
        <div class="fw-semibold" style="color:${color}">${category}</div>
      </div>
      <div class="text-muted small flex-fill">${advice}</div>
      ${a ? `<div class="text-muted small">Age: ${a} yrs</div>` : ''}
    </div>
  `;
  el.classList.remove('d-none');
}

// ---- Scroll reveal (simple IntersectionObserver) ----
document.addEventListener('DOMContentLoaded', () => {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.glass-card, .feature-card, .step-card, .history-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    obs.observe(el);
  });
});

// ============================================================
// history.js – History Page: Chart & Interactions
// ============================================================

// ---- Search / Filter ----
function filterHistory() {
  const query = document.getElementById('searchInput').value.toLowerCase();
  document.querySelectorAll('.history-item').forEach(item => {
    const food = item.getAttribute('data-food') || '';
    item.style.display = food.includes(query) ? '' : 'none';
  });
}

// ---- Delete Single Record ----
function deleteRecord(id, btnEl) {
  if (!confirm('Delete this prediction record?')) return;
  fetch(`/api/delete/${id}`, { method: 'DELETE' })
    .then(r => r.json())
    .then(d => {
      if (d.success) {
        // Remove parent .history-item from DOM
        const card = btnEl.closest('.history-item');
        card.style.transition = 'opacity 0.3s, transform 0.3s';
        card.style.opacity = '0';
        card.style.transform = 'scale(0.95)';
        setTimeout(() => card.remove(), 300);
      }
    })
    .catch(() => alert('Failed to delete record.'));
}

// ---- Clear All History ----
function clearHistory() {
  if (!confirm('Delete ALL prediction history? This cannot be undone.')) return;
  fetch('/api/clear-history', { method: 'DELETE' })
    .then(r => r.json())
    .then(d => { if (d.success) location.reload(); })
    .catch(() => alert('Failed to clear history.'));
}

// ---- Bar Chart (History Summary) ----
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('historyChart');
  if (!canvas || typeof historyData === 'undefined' || historyData.length === 0) return;

  // Aggregate calories by food
  const agg = {};
  historyData.forEach(r => {
    const name = r.food_name;
    agg[name] = (agg[name] || 0) + r.calories;
  });

  const labels = Object.keys(agg);
  const values = Object.values(agg);

  // Generate gradient colours
  const colours = labels.map((_, i) => {
    const hue = (i * 37) % 360;
    return `hsl(${hue},70%,60%)`;
  });

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Total Calories (kcal)',
        data: values,
        backgroundColor: colours,
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.parsed.y} kcal`
          }
        }
      },
      scales: {
        x: {
          ticks: { color: '#9898c0', font: { family: 'Space Grotesk', weight: '600' } },
          grid:  { color: 'rgba(255,255,255,0.05)' }
        },
        y: {
          ticks: { color: '#9898c0' },
          grid:  { color: 'rgba(255,255,255,0.05)' },
          title: { display: true, text: 'Calories (kcal)', color: '#9898c0' }
        }
      }
    }
  });
});

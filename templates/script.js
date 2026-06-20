const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

const skills = [
  'Python', 'C', 'C++', 'MATLAB', 'Verilog', 'SystemVerilog',
  'IoT', 'Embedded Systems', 'Signal Processing', 'Digital Design',
  'Instrumentation', 'LLMs', 'RAG', 'Hugging Face', 'Computer Vision'
];
const track = document.getElementById('track');
if (track) {
  [...skills, ...skills].forEach(skill => {
    const span = document.createElement('span');
    span.className = 'marquee-item';
    span.textContent = skill;
    track.appendChild(span);
  });
}

const reveals = document.querySelectorAll('.reveal');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
reveals.forEach(item => observer.observe(item));

const currentPage = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav-links a').forEach(link => {
  const href = link.getAttribute('href');
  if (href === currentPage || (currentPage === '' && href === 'index.html')) {
    link.classList.add('active');
  }
});

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.filter;
    document.querySelectorAll('.project-card[data-categories]').forEach(card => {
      const cats = card.dataset.categories || '';
      const show = filter === 'all' || cats.includes(filter);
      card.dataset.hidden = show ? 'false' : 'true';
    });
  });
});

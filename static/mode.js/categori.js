
const sliderContainer = document.querySelector('.slider-container');
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.slider-dot');
let currentSlide = 0;

function showSlide(index) {
  sliderContainer.style.transform = `translateX(-${index * 100}%)`;
  dots.forEach(dot => dot.classList.remove('active'));
  dots[index].classList.add('active');
}

setInterval(() => {
  currentSlide = (currentSlide + 1) % slides.length;
  showSlide(currentSlide);
}, 5000);

dots.forEach((dot, index) => {
  dot.addEventListener('click', () => {
    currentSlide = index;
    showSlide(currentSlide);
  });
});



    // Responsive sidebar
    if(window.innerWidth < 768) {
        sidebar.classList.add('hide');
      }
  
      window.addEventListener('resize', function() {
        if(this.innerWidth < 768) {
          sidebar.classList.add('hide');
        } else {
          sidebar.classList.remove('hide');
        }
      });
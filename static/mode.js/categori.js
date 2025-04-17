
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


      const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

      allSideMenu.forEach(item=> {
          const li = item.parentElement;
          item.addEventListener('click', function () {
              allSideMenu.forEach(i=> {
                  i.parentElement.classList.remove('active');
              })
              li.classList.add('active');
          })
      });
      
      // TOGGLE SIDEBAR
      const menuBar = document.querySelector('#content nav .bx.bx-menu');
      const sidebar = document.getElementById('sidebar');
      
      menuBar.addEventListener('click', function () {
          sidebar.classList.toggle('hide');
      })
      
      const searchButton = document.querySelector('#content nav form .form-input button');
      const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
      const searchForm = document.querySelector('#content nav form');
      
      searchButton.addEventListener('click', function (e) {
          if(window.innerWidth < 576) {
              e.preventDefault();
              searchForm.classList.toggle('show');
              if(searchForm.classList.contains('show')) {
                  searchButtonIcon.classList.replace('bx-search', 'bx-x');
              } else {
                  searchButtonIcon.classList.replace('bx-x', 'bx-search');
              }
          }
      })
      
      if(window.innerWidth < 768) {
          sidebar.classList.add('hide');
      } else if(window.innerWidth > 576) {
          searchButtonIcon.classList.replace('bx-x', 'bx-search');
          searchForm.classList.remove('show');
      }
      
      window.addEventListener('resize', function () {
          if(this.innerWidth > 576) {
              searchButtonIcon.classList.replace('bx-x', 'bx-search');
              searchForm.classList.remove('show');
          }
      })
      
      const switchMode = document.getElementById('switch-mode');
      
      switchMode.addEventListener('change', function () {
          if(this.checked) {
              document.body.classList.add('dark');
          } else {
              document.body.classList.remove('dark');
          }
      })
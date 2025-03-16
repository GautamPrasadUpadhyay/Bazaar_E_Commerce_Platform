let currentIndex = 0;
const slides = document.querySelectorAll('.slide');
const totalSlides = slides.length;
const dots = document.querySelectorAll('.dot');

function showSlide(index) {
    if (index >= totalSlides) currentIndex = 0;
    else if (index < 0) currentIndex = totalSlides - 1;
    else currentIndex = index;
    document.getElementById('slider').style.transform = `translateX(-${currentIndex * 100}%)`;
    updateDots();
}

function nextSlide() { showSlide(currentIndex + 1); }
function prevSlide() { showSlide(currentIndex - 1); }
function setSlide(index) { showSlide(index); }

function updateDots() {
    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === currentIndex);
    });
}

setInterval(nextSlide, 3000); // Auto slide every 3 seconds
updateDots();


document.addEventListener("DOMContentLoaded", () => {
    const wrapper = document.querySelector(".testimonials-wrapper");
    const testimonials = document.querySelectorAll(".testimonial");
    const prevBtn = document.querySelector(".prev-testimony");
    const nextBtn = document.querySelector(".next-testimony");
    
    let currentIndex = 0;
    const totalTestimonials = testimonials.length;
    const testimonialHeight = testimonials[0].offsetHeight; // Height of one testimonial

    // Function to update the slider position
    function updateSlider() {
        wrapper.style.transform = `translateY(-${currentIndex * testimonialHeight}px)`;
    }

    // Next button (move down)
    nextBtn.addEventListener("click", () => {
        currentIndex++;
        if (currentIndex >= totalTestimonials) {
            currentIndex = 0; // Loop back to the first testimonial
        }
        updateSlider();
    });

    // Previous button (move up)
    prevBtn.addEventListener("click", () => {
        currentIndex--;
        if (currentIndex < 0) {
            currentIndex = totalTestimonials - 1; // Loop to the last testimonial
        }
        updateSlider();
    });

    // Optional: Auto-slide every 5 seconds
    setInterval(() => {
        currentIndex++;
        if (currentIndex >= totalTestimonials) {
            currentIndex = 0;
        }
        updateSlider();
    }, 5000);
});
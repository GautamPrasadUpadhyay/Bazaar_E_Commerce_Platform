

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
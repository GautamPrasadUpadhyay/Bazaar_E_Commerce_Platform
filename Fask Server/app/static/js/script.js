document.addEventListener("DOMContentLoaded", function () {
    const testimonials = document.querySelectorAll(".testimonial");
    const prevButton = document.querySelector(".prev-testimony");
    const nextButton = document.querySelector(".next-testimony");
    let currentIndex = 0;

    function updateTestimonials() {
        testimonials.forEach((testimonial, index) => {
            testimonial.classList.remove("active");
            testimonial.style.display = "none";
        });

        testimonials[currentIndex].classList.add("active");
        testimonials[currentIndex].style.display = "block";
    }

    prevButton.addEventListener("click", function () {
        currentIndex = (currentIndex === 0) ? testimonials.length - 1 : currentIndex - 1;
        updateTestimonials();
    });

    nextButton.addEventListener("click", function () {
        currentIndex = (currentIndex === testimonials.length - 1) ? 0 : currentIndex + 1;
        updateTestimonials();
    });

    updateTestimonials(); // Initialize display
});

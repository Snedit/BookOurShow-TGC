document.addEventListener('DOMContentLoaded', () => {
    const movies = document.querySelectorAll('.movie');

    movies.forEach(movie => {
        movie.addEventListener('click', () => {
            const movieTitle = movie.querySelector('h3').innerText;
            const movieDetail = movie.querySelector('.detail').innerText;
            const movieRating = movie.querySelector('.card-body p').innerText;
            const moviePosterSrc = movie.querySelector('img').src;

            showDetails(movieTitle, movieDetail, movieRating, moviePosterSrc);
        });
    });
});

function showDetails(title, detail, rating, posterSrc) {
    const specialForm = document.querySelector('.specialContainer');
    specialForm.innerHTML = `
            <button id="cross" onclick="HideSpecialForm()">x</button>
            <img src="${posterSrc}" alt="${title}" class="details-poster">
            <h2>${title}</h2>
            <p>${detail}</p>
            <p>${rating}</p>
            <button class="book-show-btn">Book <img id="myLogo" src="static/img/fav.png"> Show</button>
        
    `;
    specialForm.style.display = 'flex'; // Ensure the form is visible
    setTimeout(() => {
        
        specialForm.style.opacity= '1'; // Ensure the form is visible
    }, 100);

}


function HideSpecialForm() {
    const specialForm = document.querySelector('.specialContainer');

    specialForm.style.opacity= '0'; // Hide the form
    setTimeout(() => {
        
        specialForm.style.display = 'none'; // Hide the form
    }, 500);
}
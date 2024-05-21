
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


function showHistory() {
    fetch('/booking_history')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const bookings = data.bookings;
                const historyContainer = document.querySelector('.historyContainer');
                

                historyContainer.innerHTML = '';  // Clear existing content

                historyContainer.innerHTML+=   `<button id="cross" onclick="document.querySelector('.historyContainer').style.display ='none'">x</button>`;
                bookings.forEach(booking => {
                    const bookingCard = `

                        <div class="booking-card" >
                            <img class= "posterBGticket" src="${booking.poster}">
                            <span>
                            <h2 class="ticketHead">${booking.title}</h2>
                            <p class="genre">${booking.detail}</p>
                            <p ><b>Tickets:</b> ${booking.ticket_count}</p>
                            <p><b>Total Cost:</b> ₹${booking.total_cost}</p>
                            <p><b>Date: </b>${booking.timestamp}</p>
                            </span>
                        </div>
                    `;

                    historyContainer.innerHTML += bookingCard;
                }
            )
            ;
            historyContainer.style.display = "grid";
            historyContainer.style.opacity= 1;

            } else {
                alert('Error fetching booking history: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching booking history:', error);
            alert('Error fetching booking history.');
        });
}


function showDetails(title, detail, rating, posterSrc) {
    const specialForm = document.querySelector('.specialContainer');
    specialForm.innerHTML = `
            <button id="cross" onclick="HideSpecialForm()">x</button>
            <img src="${posterSrc}" alt="${title}" class="details-poster">
            <h2>${title}</h2>
            <p>${detail}</p>
            <p>${rating}</p>
            <button class="book-show-btn" onclick="bookShow('${title}', '${detail}', '${posterSrc}')">Book <img id="myLogo" src="static/img/fav.png"> Show</button>
        
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


function bookShow(title, detail, posterSrc) {
    fetch('/user-details')
        .then(response => response.json())
        .then(data => {
            const user = data.user;
            const ticketCost = Math.floor(Math.random() * (500 - 300 + 1)) + 300;
            const totalCost = ticketCost;  // Initialize with single ticket cost

            const specialForm = document.querySelector('.specialContainer');
            specialForm.innerHTML = `
            <button id="cross" onclick="HideSpecialForm()">x</button>
            <div id="ticket-holder">
            <img src="${posterSrc}" id="posterTicket">
                
                <h2>${title}</h2>
                <p>${detail}</p>
                <p>Ticket Cost: ₹${ticketCost}</p>
                <div>
                    <label for="ticket-count">Number of Tickets: </label>
                    <input type="number" id="ticket-count" name="ticket-count" value="1" min="1" style="width: 60px;" onchange="updateCost(${ticketCost}, ${user.points})">
                </div>
                <p>Total Cost: ₹<span id="total-cost">${totalCost}</span></p>
                <h3>User Details</h3>
                <p>Name: ${user.username}</p>
                <p>Email: ${user.email}</p>
                <p>Phone No: +91 ${user.phone}</p>
                <button class="confirm-btn" onclick="confirmBooking('${title}', '${detail}', ${ticketCost}, '${posterSrc}')">Confirm</button>
                <p id="balance-message" style="display: none;">You don't have enough points to buy this ticket <button onclick="showAddPointsForm();">Add points</button></p>
            </div>
        `;

            // Initial check for user balance
            const confirmButton = document.querySelector('.confirm-btn');
            const message = document.getElementById('balance-message');
            if (user.points >= totalCost) {
                confirmButton.style.display = 'block';
                message.style.display = 'none';
            } else {
                confirmButton.style.display = 'none';
                message.style.display = 'block';
            }

            specialForm.style.display = 'flex'; // Ensure the form is visible
        })
        .catch(error => alert('Error fetching user details:', error));
}


function updateCost(ticketCost, userPoints) {
    const ticketCount = document.getElementById('ticket-count').value;
    const totalCost = ticketCount * ticketCost;
    document.getElementById('total-cost').innerText = totalCost;

    const confirmButton = document.querySelector('.confirm-btn');
    const message = document.getElementById('balance-message');

    if (userPoints >= totalCost) {
        confirmButton.style.display = 'block';
        message.style.display = 'none';
    } else {
        confirmButton.style.display = 'none';
        message.style.display = 'block';
    }
}

function confirmBooking(title, detail, ticketCost, poster) {
    const ticketCount = parseInt(document.getElementById('ticket-count').value);
    const totalCost = ticketCount * ticketCost;

    fetch('/confirm_booking', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: title,
            detail: detail,
            ticketCost: ticketCost,
            ticketCount: ticketCount,
            poster: poster
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            playSound("success-sound");
            updateUserPoints(data.newPoints);  // Update points in the UI
            document.querySelector("#cross").click();
            alert(`Booking confirmed for ${title}!\nTotal Cost: ₹${totalCost}`);
            // Fetch the ticket image
           
            fetch('/generate_ticket', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    detail: detail,
                    ticketCount: ticketCount,
                    totalCost: totalCost
                })
            })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                } else {
                    throw new Error('Failed to generate ticket');
                }
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'ticket.png';  // Specify the filename
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                console.log("Your ticket is downloading");
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error generating ticket: ' + error.message);
            });

        } else {
            alert(`Booking failed: ${data.message}`);
        }
    })
    .catch(error => {
        alert('Error confirming booking: ' + error.message);
    });
}







function showAddPointsForm() {
    const specialForm = document.querySelector('.specialContainer');
    specialForm.innerHTML = `
        <div id="points-form-holder">
            <button id="cross" onclick="HideSpecialForm()">x</button>
            <h2>Add Points</h2>
            <form id="addPointsForm">
                <label for="points">Enter points to add:</label>
                <input type="number" id="points" name="points" min="1" value ="500" required>
                <button id='addpointsSUBMIT' type="submit">Add Points</button>
            </form>
            <p id="points-message" style="display:none;"></p>
        </div>
    `;
    specialForm.style.display = 'flex'; // Ensure the form is visible

    // Handle form submission
    $('#addPointsForm').submit(function(event) {
        event.preventDefault();
        const points = $('#points').val();
        
        $.ajax({
            url: '/add_points',
            method: 'POST',
            data: { points: points },
            success: function(response) {
                if (response.success) {
                    
                    $('#points-message').text('Points added successfully!')
                    .removeClass('error-message')
                    .addClass('success-message')
                    .show();

                    playSound('success-sound');

                    updateUserPoints(response.newPoints);
                } else {
                    $('#points-message').text('Error adding points. Please try again.')
                    .removeClass('success-message')
                    .addClass('error-message')
                    .show();
                }
            },
            error: function() {
                $('#points-message').text('Error adding points. Please try again.').show();
            }
        });
    });
}


function updateUserPoints(newPoints) {
    // Update the user's points in the UI. Assuming you have a span with id "user-points" to display points
    $('.points').text(newPoints);
}


function playSound(soundId) {
    const sound = document.getElementById(soundId);
    if (sound) {
        sound.play();
    }
}

function animatelil()

{
    const ican = document.getElementById("ican");
    
    ican.classList.add("ghumar");
    setTimeout(() => {
        
        ican.classList.remove("ghumar");
    }, 1000);
}
document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let selectedSeat = document.querySelector('.seat.selected');
    const allSeats = document.querySelectorAll('.seat.available');
    const filterButtons = document.querySelectorAll('.filter-button');
    const selectedSeatNumber = document.getElementById('selected-seat-number');
    
    // Seat selection functionality
    allSeats.forEach(seat => {
        seat.addEventListener('click', function() {
            // Remove selection from previously selected seat
            if (selectedSeat && selectedSeat !== this) {
                selectedSeat.classList.remove('selected');
            }
            
            // Toggle selection on clicked seat
            this.classList.toggle('selected');
            
            // Update selected seat reference
            selectedSeat = this.classList.contains('selected') ? this : null;
            
            // Update selected seat information
            updateSelectedSeatInfo();
        });
    });
    
    // Filter functionality
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button state
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filter = this.getAttribute('data-filter');
            
            // Show/hide seats based on filter
            allSeats.forEach(seat => {
                const seatType = seat.getAttribute('data-type');
                
                if (filter === 'all' || seatType === filter) {
                    seat.style.display = 'block';
                } else {
                    seat.style.display = 'none';
                }
            });
            
            // Hide booked seats when filtering
            document.querySelectorAll('.seat.booked').forEach(seat => {
                if (filter !== 'all') {
                    seat.style.display = 'none';
                } else {
                    seat.style.display = 'block';
                }
            });
        });
    });
    
    // Update selected seat information display
    function updateSelectedSeatInfo() {
        if (selectedSeat) {
            const seatId = selectedSeat.getAttribute('data-seat');
            const seatType = selectedSeat.getAttribute('data-type');
            
            // Update seat number display
            if (selectedSeatNumber) {
                selectedSeatNumber.textContent = seatId;
            }
            
            // Update other seat info based on type
            let typeText = 'Standard';
            let featuresText = 'Power outlet, good visibility';
            
            if (seatType === 'accessible') {
                typeText = 'Accessible';
                featuresText = 'Wheelchair accessible, extra space, power outlet';
            } else if (seatType === 'quiet') {
                typeText = 'Quiet Zone';
                featuresText = 'Reduced noise area, power outlet, good visibility';
            }
            
            // Update type and features in UI
            const infoValues = document.querySelectorAll('.info-value');
            if (infoValues.length >= 2) {
                infoValues[1].textContent = typeText;
                infoValues[3].textContent = featuresText;
            }
            
            // Store selected seat in localStorage
            localStorage.setItem('selectedSeat', seatId);
        }
    }
    
    // Initialize with selected seat info if available
    if (selectedSeat) {
        updateSelectedSeatInfo();
    }
});
    
const roomGrid = document.querySelector('.room-grid');
const selectedBlock = document.getElementById('selected-block');
const selectedFloor = document.getElementById('selected-floor');
const selectedRoom = document.getElementById('selected-room');
const confirmButton = document.getElementById('confirm-location');
const roomPlaceholder = document.querySelector('.room-placeholder');

let currentFloor = 1;
let selectedBlockValue = null;
let selectedRoomValue = null;

function generateRooms(floor) {
    roomGrid.innerHTML = '';
    
    if (!selectedBlockValue) {
        const placeholder = document.createElement('div');
        placeholder.className = 'room-placeholder';
        placeholder.textContent = 'Please select a block first';
        roomGrid.appendChild(placeholder);
        return;
    }

    for (let i = 1; i <= 15; i++) {
        const roomBtn = document.createElement('button');
        roomBtn.className = 'room-btn';
        roomBtn.dataset.room = i;
        const roomNumber = i.toString().padStart(2, '0');
        roomBtn.textContent = `${selectedBlockValue}${floor}-${roomNumber}`;
        
        roomBtn.addEventListener('click', () => {
            document.querySelectorAll('.room-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            roomBtn.classList.add('active');
            selectedRoomValue = roomBtn.textContent;
            selectedRoom.textContent = selectedRoomValue;
            
            checkConfirmation();
        });
        
        roomGrid.appendChild(roomBtn);
    }
}

generateRooms(currentFloor);

document.querySelectorAll('.block-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.block-btn').forEach(b => {
            b.classList.remove('active');
        });
        
        btn.classList.add('active');
        selectedBlockValue = btn.dataset.block;
        selectedBlock.textContent = `Blk ${selectedBlockValue}`;
        
        generateRooms(currentFloor);
        
        selectedRoomValue = null;
        selectedRoom.textContent = 'Not selected';
        
        checkConfirmation();
    });
});

document.querySelectorAll('.floor-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.floor-btn').forEach(f => {
            f.classList.remove('active');
        });
        
        btn.classList.add('active');
        currentFloor = parseInt(btn.dataset.floor);
        selectedFloor.textContent = currentFloor;
        
        generateRooms(currentFloor);
        
        selectedRoomValue = null;
        selectedRoom.textContent = 'Not selected';
        
        checkConfirmation();
    });
});

function checkConfirmation() {
    if (selectedBlockValue && selectedRoomValue) {
        confirmButton.removeAttribute('disabled');
    } else {
        confirmButton.setAttribute('disabled', 'true');
    }
}
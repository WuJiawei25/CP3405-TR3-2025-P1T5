// 模拟不同课程的座位占用数据（0-100%）
const seatOccupancyData = {
    "CP3405-LA": [
        [85, 90, 70, 40, 30, 20], // A行
        [95, 100, 80, 60, 45, 35], // B行
        [60, 75, 90, 85, 70, 50], // C行
        [30, 45, 60, 70, 55, 40], // D行
        [20, 30, 40, 50, 35, 25]  // E行
    ],
    "CP3405-PA": [
        [40, 30, 20, 10, 5, 0],
        [50, 40, 30, 20, 15, 5],
        [60, 50, 40, 30, 25, 15],
        [70, 60, 50, 40, 35, 25],
        [80, 70, 60, 50, 45, 35]
    ],
    "CP3405-PB": [
        [20, 25, 30, 35, 40, 45],
        [15, 20, 25, 30, 35, 40],
        [10, 15, 20, 25, 30, 35],
        [5, 10, 15, 20, 25, 30],
        [0, 5, 10, 15, 20, 25]
    ]
};

// 获取DOM元素
const heatmapModal = document.getElementById('heatmapModal');
const closeModalBtn = document.querySelector('.close-modal');
const viewHeatmapBtns = document.querySelectorAll('.view-heatmap-btn');
const heatmapSeats = document.getElementById('heatmapSeats');
const modalLectureTitle = document.getElementById('modalLectureTitle');
const modalLectureTime = document.getElementById('modalLectureTime');
const modalLectureRoom = document.getElementById('modalLectureRoom');

// 关闭模态框
closeModalBtn.addEventListener('click', () => {
    heatmapModal.style.display = 'none';
});

// 点击模态框外部关闭
window.addEventListener('click', (e) => {
    if (e.target === heatmapModal) {
        heatmapModal.style.display = 'none';
    }
});

// 为每个查看热力图按钮添加事件
viewHeatmapBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        // 获取当前课程信息
        const scheduleItem = e.target.closest('.schedule-item');
        const lectureId = scheduleItem.dataset.lectureId;
        const lectureTitle = scheduleItem.querySelector('h4').textContent;
        const lectureTime = scheduleItem.querySelector('.schedule-status').textContent;
        const lectureRoom = scheduleItem.querySelector('.detail-item span').textContent;
        
        // 更新模态框信息
        modalLectureTitle.textContent = lectureTitle;
        modalLectureTime.textContent = lectureTime;
        modalLectureRoom.textContent = lectureRoom;
        
        // 生成热力图座位
        generateHeatmapSeats(lectureId);
        
        // 显示模态框
        heatmapModal.style.display = 'flex';
    });
});

// 生成热力图座位
function generateHeatmapSeats(lectureId) {
    // 清空现有座位
    heatmapSeats.innerHTML = '';
    
    // 获取对应课程的占用数据
    const occupancyData = seatOccupancyData[lectureId];
    if (!occupancyData) return;
    
    // 生成座位行
    occupancyData.forEach((row, rowIndex) => {
        const seatRow = document.createElement('div');
        seatRow.className = 'seat-row';
        
        // 每行中间添加过道（第3和第4个座位之间）
        row.forEach((occupancy, colIndex) => {
            const seat = document.createElement('div');
            seat.className = 'seat';
            
            // 根据占用率设置座位颜色类别
            if (occupancy <= 30) {
                seat.classList.add('low-occupancy');
            } else if (occupancy <= 70) {
                seat.classList.add('medium-occupancy');
            } else {
                seat.classList.add('high-occupancy');
            }
            
            // 显示占用率百分比
            const occupancyText = document.createElement('span');
            occupancyText.className = 'seat-icon';
            occupancyText.textContent = `${occupancy}%`;
            seat.appendChild(occupancyText);
            
            seatRow.appendChild(seat);
            
            // 在第3个座位后添加过道
            if (colIndex === 2) {
                const aisle = document.createElement('div');
                aisle.className = 'aisle';
                seatRow.appendChild(aisle);
            }
        });
        
        heatmapSeats.appendChild(seatRow);
    });
}

// 日程筛选功能
const filterButtons = document.querySelectorAll('.filter-button');
filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        // 移除所有活跃状态
        filterButtons.forEach(b => b.classList.remove('active'));
        // 添加当前按钮活跃状态
        btn.classList.add('active');
        
        // 这里可以添加实际筛选逻辑
        const filter = btn.dataset.filter;
        console.log(`Filtering schedule by: ${filter}`);
    });
});
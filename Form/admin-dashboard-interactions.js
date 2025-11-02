// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 1. 任务项悬停效果
    const taskItems = document.querySelectorAll('.task-item');
    taskItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'translateY(-2px)';
            item.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
            item.style.transition = 'all 0.3s ease';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.transform = 'translateY(0)';
            item.style.boxShadow = 'none';
        });
    });

    // 2. 任务操作按钮加载状态
    const actionButtons = document.querySelectorAll('.task-action');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // 如果按钮有跳转链接则不添加加载状态（已有的跳转按钮）
            if (!this.hasAttribute('onclick')) {
                e.preventDefault();
                const originalText = this.textContent;
                this.textContent = 'Processing...';
                this.disabled = true;
                
                // 模拟处理延迟
                setTimeout(() => {
                    this.textContent = originalText;
                    this.disabled = false;
                    // 这里可以添加实际处理逻辑，比如AJAX请求
                }, 1500);
            }
        });
    });

    // 3. 统计数据动态更新（模拟实时数据）
    function updateStats() {
        const stats = {
            reservations: Math.floor(Math.random() * 50) + 100, // 100-150之间
            activeUsers: Math.floor(Math.random() * 30) + 50,   // 50-80之间
            roomsInUse: `${Math.floor(Math.random() * 15) + 10}/40` // 10-25/40
        };

        document.querySelector('.stat-value').textContent = stats.reservations;
        document.querySelectorAll('.stat-value')[1].textContent = stats.activeUsers;
        document.querySelectorAll('.stat-value')[2].textContent = stats.roomsInUse;
    }

    // 初始更新一次
    updateStats();
    // 每30秒更新一次统计数据（模拟实时刷新）
    setInterval(updateStats, 30000);

    // 4. 左侧导航按钮活跃状态
    const navLinks = document.querySelectorAll('.home_left-buttons a');
    const currentPath = window.location.pathname;
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath.split('/').pop()) {
            link.querySelector('button').classList.add('active');
        }
    });

    // 5. 登出确认
    const logoutLink = document.querySelector('.back-arrow a');
    logoutLink.addEventListener('click', function(e) {
        const confirmLogout = confirm('Are you sure you want to log out?');
        if (!confirmLogout) {
            e.preventDefault(); // 取消跳转
        }
    });
});
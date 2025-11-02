// 等待页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
  // 解锁按钮交互
  const unlockBtn = document.querySelector('.unlock-btn');
  if (unlockBtn) {
    unlockBtn.addEventListener('click', handleUnlock);
  }

  // 预约按钮交互
  const reserveBtn = document.querySelector('.reserve-btn');
  if (reserveBtn) {
    reserveBtn.addEventListener('click', handleReserve);
  }

  // 查看预约按钮交互
  const checkReserveBtn = document.querySelector('.check-reserve-btn');
  if (checkReserveBtn) {
    checkReserveBtn.addEventListener('click', handleCheckReserve);
  }

  // 用户图标点击交互
  const userIcon = document.querySelector('.user-icon');
  if (userIcon) {
    userIcon.addEventListener('click', showUserMenu);
  }
});

// 解锁功能处理
function handleUnlock() {
  const btn = this;
  // 防止重复点击
  if (btn.classList.contains('unlocking')) return;

  // 添加动画状态
  btn.classList.add('unlocking');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin lock-icon"></i> UNLOCKING...';

  // 模拟解锁过程（1.5秒后完成）
  setTimeout(() => {
    btn.classList.remove('unlocking');
    btn.innerHTML = '<i class="fas fa-check lock-icon"></i> UNLOCKED';
    
    // 2秒后恢复原始状态
    setTimeout(() => {
      btn.innerHTML = '<i class="fas fa-lock-open lock-icon"></i> UNLOCK';
    }, 2000);
  }, 1500);
}

// 预约功能处理
function handleReserve() {
  const btn = this;
  if (btn.classList.contains('reserving')) return;

  btn.classList.add('reserving');
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Reserving...';

  // 模拟预约过程（1.5秒后完成）
  setTimeout(() => {
    btn.classList.remove('reserving');
    btn.innerHTML = 'Reserve';
    showNotification('Reservation submitted successfully!', 'success');
  }, 1500);
}

// 查看预约处理
function handleCheckReserve() {
  // 模拟跳转到预约记录页面（实际项目中替换为真实路由）
  showNotification('Redirecting to your reservations...', 'info');
  setTimeout(() => {
    window.location.href = 'my_reservations.html'; // 假设的预约记录页面
  }, 1000);
}

// 用户菜单显示（点击用户图标时）
function showUserMenu() {
  let userMenu = document.querySelector('.user-menu');
  if (userMenu) {
    userMenu.remove();
    return;
  }

  // 创建用户菜单
  userMenu = document.createElement('div');
  userMenu.className = 'user-menu';
  userMenu.innerHTML = `
    <div class="menu-item"><i class="fas fa-user-circle"></i> Profile</div>
    <div class="menu-item"><i class="fas fa-cog"></i> Settings</div>
    <div class="menu-item"><i class="fas fa-question-circle"></i> Help</div>
    <div class="menu-item"><i class="fas fa-sign-out-alt"></i> Logout</div>
  `;

  // 添加到页面并定位在用户图标下方
  const userIcon = document.querySelector('.user-icon');
  if (userIcon && userIcon.parentNode) {
    userIcon.parentNode.appendChild(userMenu);
    const iconRect = userIcon.getBoundingClientRect();
    userMenu.style.top = `${iconRect.bottom + 10}px`;
    userMenu.style.right = `${window.innerWidth - iconRect.right}px`;

    // 点击页面其他区域关闭菜单
    const closeMenu = function(e) {
      if (!userMenu.contains(e.target) && e.target !== userIcon) {
        userMenu.remove();
        document.removeEventListener('click', closeMenu);
      }
    };
    document.addEventListener('click', closeMenu);
  }
}

// 通知提示功能（通用方法）
function showNotification(message, type = 'info') {
  // 创建通知元素
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerText = message;

  // 添加到页面
  document.body.appendChild(notification);

  // 自动消失（3秒后）
  setTimeout(() => {
    notification.classList.add('fade-out');
    setTimeout(() => notification.remove(), 500);
  }, 3000);
}
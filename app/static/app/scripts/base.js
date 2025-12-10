const toggleButton = document.getElementById('toggle-btn');
const sidebar = document.getElementById('sidebar');
const dropdownButtons = sidebar ? sidebar.querySelectorAll('.dropdown-btn') : [];
const menuIcon = document.querySelector('#menu-icon');
const profileButton = document.querySelector('#profile-button');
const navbar = document.querySelector('#navbar');
const aside = document.querySelector('aside');
const body = document.querySelector('body');

// Early return if critical elements are missing
if (!aside || !body) {
  console.warn('Critical sidebar elements not found');
}

if (toggleButton) {
  toggleButton.addEventListener('click', toggleSidebar);
}

dropdownButtons.forEach(btn => {
  btn.addEventListener('click', () => toggleSubMenu(btn));
});

if (menuIcon) {
  menuIcon.addEventListener('click', toggleSidebar);
}

if (profileButton) {
  profileButton.addEventListener('click', () => {
    if (navbar) {
      navbar.classList.toggle('active');
    }
  });
}

const homeContentLeft = document.querySelector('.home-content-left');
const homeContentRight = document.querySelector('.home-content-rigth');

function toggleSidebar() {
  if (!aside || !body) return;
  
  if (aside.classList.contains('active')) {
    aside.classList.remove('active');
    aside.classList.add('close');

    body.classList.remove('active');
    if (homeContentLeft) homeContentLeft.classList.remove('active');
    if (homeContentRight) homeContentRight.classList.remove('active');
  } else {
    aside.classList.add('active');
    aside.classList.remove('close');

    body.classList.add('active');
    if (homeContentLeft) homeContentLeft.classList.add('active');
    if (homeContentRight) homeContentRight.classList.add('active');
  }
  closeAllSubMenus();
}


function toggleSubMenu(button) {
  const submenu = button.nextElementSibling;
  if (!submenu) return;

  if (!submenu.classList.contains('show')) {
    closeAllSubMenus();
  }

  submenu.classList.toggle('show');
  button.classList.toggle('rotate');

  if (sidebar && sidebar.classList.contains('close')) {
    sidebar.classList.remove('close');
    if (toggleButton) {
      toggleButton.classList.remove('rotate');
    }
  }
}

function closeAllSubMenus() {
  if (!sidebar) return;
  sidebar.querySelectorAll('.sub-menu.show').forEach(submenu => {
    submenu.classList.remove('show');
    const button = submenu.previousElementSibling;
    if (button && button.classList.contains('dropdown-btn')) {
      button.classList.remove('rotate');
    }
  });
}

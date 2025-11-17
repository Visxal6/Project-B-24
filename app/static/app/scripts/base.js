const toggleButton = document.getElementById('toggle-btn');
const sidebar = document.getElementById('sidebar');
const dropdownButtons = sidebar.querySelectorAll('.dropdown-btn');
const menuIcon = document.querySelector('#menu-icon');
const profileButton = document.querySelector('#profile-button')
const navbar = document.querySelector('#navbar');
const aside = document.querySelector('aside');
const body = document.querySelector('body');

toggleButton.addEventListener('click', toggleSidebar);

dropdownButtons.forEach(btn => {
  btn.addEventListener('click', () => toggleSubMenu(btn));
});

menuIcon.addEventListener('click', toggleSidebar);

profileButton.addEventListener('click', () => {
  navbar.classList.toggle('active');
})

const homeContentLeft = document.querySelector('.home-content-left');
const homeContentRight = document.querySelector('.home-content-rigth');

function toggleSidebar() {
  if (aside.classList.contains('active')) {
    aside.classList.remove('active');
    aside.classList.add('close');

    body.classList.remove('active');
    homeContentLeft.classList.remove('.active');
    homeContentRight.classList.remove('.active');
  } else {
    aside.classList.add('active');
    aside.classList.remove('close');

    body.classList.add('active');
    homeContentLeft.classList.add('.active');
    homeContentRight.classList.add('.active');
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

  if (sidebar.classList.contains('close')) {
    sidebar.classList.remove('close');
    toggleButton.classList.remove('rotate');
  }
}

function closeAllSubMenus() {
  sidebar.querySelectorAll('.sub-menu.show').forEach(submenu => {
    submenu.classList.remove('show');
    const button = submenu.previousElementSibling;
    if (button && button.classList.contains('dropdown-btn')) {
      button.classList.remove('rotate');
    }
  });
}

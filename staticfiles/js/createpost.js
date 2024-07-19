document.querySelector('.hamburger').addEventListener('click', function() {
    var sidebar = document.querySelector('.sidebar');
    var ariaExpanded = this.getAttribute('aria-expanded') === 'true';
    this.setAttribute('aria-expanded', !ariaExpanded);
    sidebar.classList.toggle('show');
    sidebar.setAttribute('aria-hidden', ariaExpanded);
});

document.querySelector('.close-btn').addEventListener('click', function() {
    var sidebar = document.querySelector('.sidebar');
    var hamburger = document.querySelector('.hamburger');
    sidebar.classList.remove('show');
    sidebar.setAttribute('aria-hidden', 'true');
    hamburger.setAttribute('aria-expanded', 'false');
});

document.querySelector('#user-email').addEventListener('click', function() {
    var popup = document.querySelector('#email-popup');
    var isHidden = popup.getAttribute('aria-hidden') === 'true';
    popup.style.display = isHidden ? 'flex' : 'none';
    popup.setAttribute('aria-hidden', !isHidden);
});

document.addEventListener('click', function(event) {
    var popup = document.querySelector('#email-popup');
    var userInfo = document.querySelector('.user-info');
    if (!userInfo.contains(event.target)) {
        popup.style.display = 'none';
        popup.setAttribute('aria-hidden', 'true');
    }
});


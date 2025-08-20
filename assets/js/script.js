'use strict';



// element toggle function
const elementToggleFunc = function (elem) { elem.classList.toggle("active"); }



// sidebar variables
const sidebar = document.querySelector("[data-sidebar]");
const sidebarBtn = document.querySelector("[data-sidebar-btn]");

// sidebar toggle functionality for mobile
sidebarBtn.addEventListener("click", function () { elementToggleFunc(sidebar); });



// testimonials variables
const testimonialsItem = document.querySelectorAll("[data-testimonials-item]");
const modalContainer = document.querySelector("[data-modal-container]");
const modalCloseBtn = document.querySelector("[data-modal-close-btn]");
const overlay = document.querySelector("[data-overlay]");

// modal variable
const modalImg = document.querySelector("[data-modal-img]");
const modalTitle = document.querySelector("[data-modal-title]");
const modalText = document.querySelector("[data-modal-text]");

// modal toggle function
const testimonialsModalFunc = function () {
  modalContainer.classList.toggle("active");
  overlay.classList.toggle("active");
}

// add click event to all modal items
for (let i = 0; i < testimonialsItem.length; i++) {

  testimonialsItem[i].addEventListener("click", function () {

    modalImg.src = this.querySelector("[data-testimonials-avatar]").src;
    modalImg.alt = this.querySelector("[data-testimonials-avatar]").alt;
    modalTitle.innerHTML = this.querySelector("[data-testimonials-title]").innerHTML;
    modalText.innerHTML = this.querySelector("[data-testimonials-text]").innerHTML;

    testimonialsModalFunc();

  });

}

// add click event to modal close button
modalCloseBtn.addEventListener("click", testimonialsModalFunc);
overlay.addEventListener("click", testimonialsModalFunc);



// custom select variables
const select = document.querySelector("[data-select]");
const selectItems = document.querySelectorAll("[data-select-item]");
const selectValue = document.querySelector("[data-selecct-value]");
const filterBtn = document.querySelectorAll("[data-filter-btn]");

select.addEventListener("click", function () { elementToggleFunc(this); });

// add event in all select items
for (let i = 0; i < selectItems.length; i++) {
  selectItems[i].addEventListener("click", function () {

    let selectedValue = this.innerText.toLowerCase();
    selectValue.innerText = this.innerText;
    elementToggleFunc(select);
    filterFunc(selectedValue);

  });
}

// filter variables
const filterItems = document.querySelectorAll("[data-filter-item]");

const filterFunc = function (selectedValue) {

  for (let i = 0; i < filterItems.length; i++) {

    if (selectedValue === "all") {
      filterItems[i].classList.add("active");
    } else if (selectedValue === filterItems[i].dataset.category) {
      filterItems[i].classList.add("active");
    } else {
      filterItems[i].classList.remove("active");
    }

  }

}

// add event in all filter button items for large screen
let lastClickedBtn = filterBtn[0];

for (let i = 0; i < filterBtn.length; i++) {

  filterBtn[i].addEventListener("click", function () {

    let selectedValue = this.innerText.toLowerCase();
    selectValue.innerText = this.innerText;
    filterFunc(selectedValue);

    lastClickedBtn.classList.remove("active");
    this.classList.add("active");
    lastClickedBtn = this;

  });

}



// contact form variables
const form = document.querySelector("[data-form]");
const formInputs = document.querySelectorAll("[data-form-input]");
const formBtn = document.querySelector("[data-form-btn]");

// add event to all form input field
for (let i = 0; i < formInputs.length; i++) {
  formInputs[i].addEventListener("input", function () {

    // check form validation
    if (form.checkValidity()) {
      formBtn.removeAttribute("disabled");
    } else {
      formBtn.setAttribute("disabled", "");
    }

  });
}

// page navigation variables
const navigationLinks = document.querySelectorAll("[data-nav-link]");
const pages = document.querySelectorAll("[data-page]");

for (let navIndex = 0; navIndex < navigationLinks.length; navIndex++) {
  navigationLinks[navIndex].addEventListener("click", function () {
    const targetPage = this.textContent.trim().toLowerCase();

    // 1. 页面切换：只有页面中匹配的激活
    pages.forEach(page => {
      const isMatch = page.dataset.page === targetPage;
      page.classList.toggle("active", isMatch);
    });

    // 2. 导航高亮：只有当前点击的按钮激活
    navigationLinks.forEach((link, idx) => {
      link.classList.toggle("active", idx === navIndex);
    });

    // 3. 手动发送 GA page_view
    const pagePath = `/${targetPage}`;
    const pageTitle = targetPage.charAt(0).toUpperCase() + targetPage.slice(1);

    console.log(`[GA] page_view sent → ${pagePath}`);
    gtag('event', 'page_view', {
      page_path: pagePath,
      page_title: pageTitle
    });

    // 可选：滚动到顶部
    window.scrollTo(0, 0);
  });
}

document.addEventListener("DOMContentLoaded", function() {
  const currentPath = window.location.pathname;

  // If it’s a pagination page (like /page2/), or the homepage but the user previously clicked on Pagination/Blog
  if (currentPath.match(/\/page\d+/) || (currentPath === "/" && sessionStorage.getItem("returnFromBlog") === "true")) {
    document.querySelectorAll(".navbar-link").forEach(el => el.classList.remove("active"));
    document.querySelectorAll("article").forEach(el => el.classList.remove("active"));

    const blogNav = document.querySelector('.navbar-link[data-nav-link][data-page="blog"]');
    const blogArticle = document.querySelector('article.blog');

    if (blogNav) blogNav.classList.add("active");
    if (blogArticle) blogArticle.classList.add("active");
  }

  // When clicking Pagination or Blog → mark so that when returning to the homepage, Blog is still displayed
  document.querySelectorAll('[data-keep-blog="true"], .navbar-link[data-page="blog"]').forEach(link => {
    link.addEventListener("click", function() {
      sessionStorage.setItem("returnFromBlog", "true");
    });
  });

  // Clear the Blog state when clicking other Navbar items
  document.querySelectorAll('.navbar-link[data-nav-link]').forEach(nav => {
    nav.addEventListener("click", function() {
      if (nav.getAttribute("data-page") !== "blog") {
        sessionStorage.removeItem("returnFromBlog");
      }
    });
  });
});

// // Page navigation variables
// const navigationLinks = document.querySelectorAll("[data-nav-link]");
// const pages = document.querySelectorAll("[data-page]");
// const pagination = document.querySelector('.pagination'); // Access the pagination control

// // Add click event to all navigation links
// for (let i = 0; i < navigationLinks.length; i++) {
//   navigationLinks[i].addEventListener("click", function () {

//     for (let j = 0; j < pages.length; j++) {
//       if (this.innerHTML.toLowerCase() === pages[j].dataset.page) {
//         pages[j].classList.add("active");
//         navigationLinks[j].classList.add("active");
//         window.scrollTo(0, 0);

//         // Show or hide the pagination control
//         if (this.innerHTML.toLowerCase() === 'blog') {
//           pagination.style.display = ''; // Show pagination when "Blog" is clicked
//         } else {
//           pagination.style.display = 'none'; // Hide pagination for other pages
//         }
//       } else {
//         pages[j].classList.remove("active");
//         navigationLinks[j].classList.remove("active");
//       }
//     }

//   });
// }


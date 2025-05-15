/**
 * Article AJAX functionality
 * Handles search, filtering, and pagination without page reloads
 */

// Store the current state of filters and pagination
let currentState = {
  search: "",
  sort: "",
  category: [],
  page: 1,
};

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Initialize the current state from URL parameters
  initializeFromUrl();

  // Set up event listeners
  setupEventListeners();

  // Initialize animation observer
  initAnimationObserver();
});

// Add this to the initializeFromUrl function to set initial visibility
function initializeFromUrl() {
  const urlParams = new URLSearchParams(window.location.search);

  currentState.search = urlParams.get("search") || "";
  currentState.sort = urlParams.get("sort") || "";
  currentState.page = Number.parseInt(urlParams.get("page") || "1");

  const categoryParam = urlParams.get("category");
  currentState.category = categoryParam ? categoryParam.split(",") : [];

  // Set initial featured article visibility based on search parameters
  const hasSearchOrFilter = Boolean(
    currentState.search || currentState.category.length > 0 || currentState.sort
  );
  updateFeaturedArticleVisibility(hasSearchOrFilter);
}

/**
 * Set up all event listeners for the page
 */
function setupEventListeners() {
  // Dropdown functionality
  setupDropdowns();

  // Search form submission
  setupSearchForm();

  // Sort selection
  setupSortSelection();

  // Category selection
  setupCategorySelection();

  // Remove filter badges
  setupFilterBadges();

  // Pagination
  setupPagination();

  // View all articles
  setupViewAllArticles();
}

/**
 * Set up dropdown functionality
 */
function setupDropdowns() {
  const filterButton = document.getElementById("filterButton");
  const filterContent = document.getElementById("filterContent");
  const categoryButton = document.getElementById("categoryButton");
  const categoryContent = document.getElementById("categoryContent");

  // Toggle filter dropdown
  filterButton.addEventListener("click", (e) => {
    e.stopPropagation();
    filterContent.classList.toggle("show");
    // Close other dropdown if open
    categoryContent.classList.remove("show");
  });

  // Toggle category dropdown
  categoryButton.addEventListener("click", (e) => {
    e.stopPropagation();
    categoryContent.classList.toggle("show");
    // Close other dropdown if open
    filterContent.classList.remove("show");
  });

  // Close dropdowns when clicking outside
  window.addEventListener("click", (event) => {
    if (
      !event.target.matches("#filterButton") &&
      !filterContent.contains(event.target)
    ) {
      filterContent.classList.remove("show");
    }
    if (
      !event.target.matches("#categoryButton") &&
      !categoryContent.contains(event.target)
    ) {
      categoryContent.classList.remove("show");
    }
  });
}

/**
 * Set up search form submission
 */
function setupSearchForm() {
  const searchForm = document.getElementById("searchForm");
  const searchInput = searchForm.querySelector('input[name="search"]');

  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const searchValue = searchInput.value.trim();
    if (searchValue !== currentState.search) {
      currentState.search = searchValue;
      currentState.page = 1; // Reset to page 1 when search changes
      fetchArticles();
    }
  });

  // Add input event for real-time search (optional, with debounce)
  let searchTimeout;
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      const searchValue = searchInput.value.trim();
      if (searchValue !== currentState.search) {
        currentState.search = searchValue;
        currentState.page = 1; // Reset to page 1 when search changes
        fetchArticles();
      }
    }, 500); // 500ms debounce
  });
}

/**
 * Set up sort selection
 */
function setupSortSelection() {
  const radioItems = document.querySelectorAll(".radio-item");

  radioItems.forEach((item) => {
    item.addEventListener("click", function () {
      const value = this.getAttribute("data-value");
      const filterType = this.getAttribute("data-filter-type");

      if (filterType === "sort" && value !== currentState.sort) {
        currentState.sort = value;
        fetchArticles();
      }

      // Close dropdown after selection
      document.getElementById("filterContent").classList.remove("show");
    });
  });
}

/**
 * Set up category selection
 */
function setupCategorySelection() {
  const categoryCheckboxes = document.querySelectorAll(
    'input[name="category"]'
  );

  categoryCheckboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      // Get all selected categories
      const selectedCategories = Array.from(
        document.querySelectorAll('input[name="category"]:checked')
      ).map((cb) => cb.value);

      // Update state if changed
      if (
        JSON.stringify(selectedCategories) !==
        JSON.stringify(currentState.category)
      ) {
        currentState.category = selectedCategories;
        currentState.page = 1; // Reset to page 1 when categories change
        fetchArticles();
      }

      // Close dropdown after selection
      document.getElementById("categoryContent").classList.remove("show");
    });
  });
}

/**
 * Set up filter badge removal
 */
function setupFilterBadges() {
  // This will be called after each content update to attach new event listeners
  function attachFilterBadgeListeners() {
    const removeFilterButtons = document.querySelectorAll(".remove-filter");

    removeFilterButtons.forEach((button) => {
      button.addEventListener("click", function () {
        const badge = this.parentElement;
        const filterType = badge.getAttribute("data-filter-type");
        const value = badge.getAttribute("data-value");

        // Remove this filter
        if (filterType === "search") {
          currentState.search = "";
          document.querySelector('input[name="search"]').value = "";
        } else if (filterType === "sort") {
          currentState.sort = "";
        } else if (filterType === "category") {
          // Remove category from array
          currentState.category = currentState.category.filter(
            (cat) => cat !== value
          );

          // Uncheck the corresponding checkbox
          const checkbox = document.getElementById(`category-${value}`);
          if (checkbox) checkbox.checked = false;
        }

        fetchArticles();
      });
    });
  }

  // Initial attachment
  attachFilterBadgeListeners();

  // Export for reuse after content updates
  window.attachFilterBadgeListeners = attachFilterBadgeListeners;
}

/**
 * Set up pagination
 */
function setupPagination() {
  // This will be called after each content update to attach new event listeners
  function attachPaginationListeners() {
    const paginationLinks = document.querySelectorAll(".pagination-link");

    paginationLinks.forEach((link) => {
      link.addEventListener("click", function (e) {
        e.preventDefault();

        const page = Number.parseInt(this.getAttribute("data-page"));
        if (page !== currentState.page) {
          currentState.page = page;
          fetchArticles();

          // Scroll to articles container (opsional)
        //   document
            // .getElementById("articlesContainer")
            // .scrollIntoView({ behavior: "smooth" });
        }
      });
    });
  }

  // Initial attachment
  attachPaginationListeners();

  // Export for reuse after content updates
  window.attachPaginationListeners = attachPaginationListeners;
}

/**
 * Set up view all articles link
 */
function setupViewAllArticles() {
  const viewAllLinks = document.querySelectorAll(".view-all-articles");

  viewAllLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();

      // Reset all filters
      currentState = {
        search: "",
        sort: "",
        category: [],
        page: 1,
      };

      // Reset UI
      document.querySelector('input[name="search"]').value = "";
      document
        .querySelectorAll('input[name="category"]:checked')
        .forEach((cb) => {
          cb.checked = false;
        });

      fetchArticles();
    });
  });
}

// Modify the fetchArticles function to preserve the featured article section
function fetchArticles() {
  // Show loading state
  const articlesContainer = document.getElementById("articlesContainer");
  articlesContainer.innerHTML = `<style>
.loader {
    width: 48px;
    height: 48px;
    border: 5px solid #FFF;
    border-bottom-color: #FF3D00;
    border-radius: 50%;
    display: inline-block;
    box-sizing: border-box;
    animation: rotation 1s linear infinite;
    }

    @keyframes rotation {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
    } 
</style>

<div class="col-span-3 text-center py-8">
  <span class="loader"></span>
</div>
`;

  // Build query parameters
  const params = new URLSearchParams();

  if (currentState.search) params.set("search", currentState.search);
  if (currentState.sort) params.set("sort", currentState.sort);
  if (currentState.category.length > 0)
    params.set("category", currentState.category.join(","));
  if (currentState.page > 1) params.set("page", currentState.page.toString());

  // Add AJAX parameter
  params.set("ajax", "true");

  // Fetch articles
  fetch(`${window.location.pathname}?${params.toString()}`, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      // Update articles container
      updateArticlesContainer(data.articles_html);

      // Update active filters
      updateActiveFilters(data.active_filters_html);

      // Update pagination
      updatePagination(data.pagination_html);

      // Update featured article section visibility
      updateFeaturedArticleVisibility(data.has_search_or_filter);

      // Update URL without reloading page
      updateUrl();

      // Re-initialize animation observer for new content
      initAnimationObserver();

      // Reattach event listeners to new content
      window.attachFilterBadgeListeners();
      window.attachPaginationListeners();
    })
    .catch((error) => {
      console.error("Error fetching articles:", error);
      articlesContainer.innerHTML =
        '<div class="col-span-3 text-center py-8"><p class="text-gray-600">Error loading articles. Please try again.</p></div>';
    });
}

// Modify the updateFeaturedArticleVisibility function to hide the featured article when a search query is active
function updateFeaturedArticleVisibility(hasSearchOrFilter) {
  const featuredSection = document.getElementById("featuredArticleSection");

  if (featuredSection) {
    // Hide featured article when searching/filtering with a smooth transition
    if (hasSearchOrFilter) {
      featuredSection.classList.add("featured-hidden");
      // After transition completes, set to display none
      setTimeout(() => {
        if (featuredSection.classList.contains("featured-hidden")) {
          featuredSection.style.display = "none";
        }
      }, 300); // Match this with the CSS transition duration
    } else {
      // First make it visible but with opacity 0
      featuredSection.style.display = "block";
      // Force a reflow to ensure the display change takes effect before adding the transition
      void featuredSection.offsetWidth;
      // Then remove the hidden class to trigger the fade-in transition
      featuredSection.classList.remove("featured-hidden");
    }
  }
}

/**
 * Update articles container with new HTML
 */
function updateArticlesContainer(html) {
  const articlesContainer = document.getElementById("articlesContainer");
  articlesContainer.innerHTML = html;
}

/**
 * Update active filters with new HTML
 */
function updateActiveFilters(html) {
  const activeFilters = document.getElementById("activeFilters");
  activeFilters.innerHTML = html;
}

/**
 * Update pagination with new HTML
 */
function updatePagination(html) {
  const paginationContainer = document.querySelector(".pagination-container");
  if (paginationContainer) {
    paginationContainer.innerHTML = html;
  }
}

/**
 * Update URL without reloading page
 */
function updateUrl() {
  const params = new URLSearchParams();

  if (currentState.search) params.set("search", currentState.search);
  if (currentState.sort) params.set("sort", currentState.sort);
  if (currentState.category.length > 0)
    params.set("category", currentState.category.join(","));
  if (currentState.page > 1) params.set("page", currentState.page.toString());

  const newUrl = `${window.location.pathname}${
    params.toString() ? "?" + params.toString() : ""
  }`;

  // Update URL without reloading page
  window.history.pushState({ path: newUrl }, "", newUrl);
}

/**
 * Initialize animation observer for fade-in animations
 */
function initAnimationObserver() {
  const observerOptions = {
    root: null,
    rootMargin: "0px",
    threshold: 0.1,
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("animate-fade-in-up");
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe all elements with animate-on-scroll class
  document.querySelectorAll(".animate-on-scroll").forEach((element) => {
    observer.observe(element);
  });
}

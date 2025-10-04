(function(){
  // Конвертер валют
  function round(value){
    return Math.round((value + Number.EPSILON) * 10000) / 10000;
  }

  function convert(){
    var amount = parseFloat(document.getElementById('amount').value || '0');
    var from = document.getElementById('from').value;
    var to = document.getElementById('to').value;
    var rates = window.CONVERTER_RATES || {};
    if(!rates[from] || !rates[to]){
      document.getElementById('result').value = '';
      return;
    }
    // Normalize to USD base using provided static rates
    var amountInUsd = amount / rates[from];
    var converted = amountInUsd * rates[to];
    document.getElementById('result').value = round(converted);
  }

  // Система управления валютами
  var CurrencyManager = {
    allCurrencies: [],
    filteredCurrencies: [],
    currentPage: 1,
    itemsPerPage: 5,
    
    init: function() {
      this.loadCurrencies();
      this.setupEventListeners();
      this.render();
    },
    
    loadCurrencies: function() {
      var tableBody = document.getElementById('currencyTableBody');
      if (!tableBody) return;
      
      var rows = tableBody.querySelectorAll('tr');
      this.allCurrencies = Array.from(rows).map(function(row) {
        return {
          code: row.dataset.code,
          rate: parseFloat(row.dataset.rate),
          element: row
        };
      });
      this.filteredCurrencies = [...this.allCurrencies];
    },
    
    setupEventListeners: function() {
      var searchInput = document.getElementById('currencySearch');
      var sortSelect = document.getElementById('sortBy');
      var prevBtn = document.getElementById('prevPage');
      var nextBtn = document.getElementById('nextPage');
      
      if (searchInput) {
        searchInput.addEventListener('input', this.handleSearch.bind(this));
      }
      
      if (sortSelect) {
        sortSelect.addEventListener('change', this.handleSort.bind(this));
      }
      
      if (prevBtn) {
        prevBtn.addEventListener('click', this.prevPage.bind(this));
      }
      
      if (nextBtn) {
        nextBtn.addEventListener('click', this.nextPage.bind(this));
      }
    },
    
    handleSearch: function(event) {
      var query = event.target.value.toLowerCase().trim();
      
      this.filteredCurrencies = this.allCurrencies.filter(function(currency) {
        return currency.code.toLowerCase().includes(query);
      });
      
      this.currentPage = 1;
      this.render();
    },
    
    handleSort: function(event) {
      var sortValue = event.target.value;
      var sortField = sortValue.split('-')[0];
      var sortDirection = sortValue.split('-')[1];
      
      this.filteredCurrencies.sort(function(a, b) {
        var aVal, bVal;
        
        if (sortField === 'code') {
          aVal = a.code;
          bVal = b.code;
        } else {
          aVal = a.rate;
          bVal = b.rate;
        }
        
        if (sortDirection === 'asc') {
          return aVal > bVal ? 1 : -1;
        } else {
          return aVal < bVal ? 1 : -1;
        }
      });
      
      this.currentPage = 1;
      this.render();
    },
    
    prevPage: function() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.render();
      }
    },
    
    nextPage: function() {
      var totalPages = Math.ceil(this.filteredCurrencies.length / this.itemsPerPage);
      if (this.currentPage < totalPages) {
        this.currentPage++;
        this.render();
      }
    },
    
    render: function() {
      var tableBody = document.getElementById('currencyTableBody');
      var prevBtn = document.getElementById('prevPage');
      var nextBtn = document.getElementById('nextPage');
      var pageInfo = document.getElementById('pageInfo');
      
      if (!tableBody) return;
      
      // Скрыть все строки
      this.allCurrencies.forEach(function(currency) {
        currency.element.style.display = 'none';
      });
      
      // Показать только нужные строки для текущей страницы
      var startIndex = (this.currentPage - 1) * this.itemsPerPage;
      var endIndex = startIndex + this.itemsPerPage;
      var visibleCurrencies = this.filteredCurrencies.slice(startIndex, endIndex);
      
      visibleCurrencies.forEach(function(currency) {
        currency.element.style.display = '';
      });
      
      // Обновить пагинацию
      var totalPages = Math.ceil(this.filteredCurrencies.length / this.itemsPerPage);
      
      if (prevBtn) {
        prevBtn.disabled = this.currentPage <= 1;
      }
      
      if (nextBtn) {
        nextBtn.disabled = this.currentPage >= totalPages;
      }
      
      if (pageInfo) {
        pageInfo.textContent = 'Страница ' + this.currentPage + ' из ' + totalPages;
      }
    }
  };

  // Инициализация
  document.addEventListener('DOMContentLoaded', function() {
    // Конвертер
    document.getElementById('convertBtn')?.addEventListener('click', convert);
    document.getElementById('amount')?.addEventListener('input', convert);
    document.getElementById('from')?.addEventListener('change', convert);
    document.getElementById('to')?.addEventListener('change', convert);
    
    // Управление валютами
    CurrencyManager.init();
    
    // initial calculation
    convert();
  });
})();



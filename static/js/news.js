(function() {
  'use strict';

  var NewsManager = {
    config: window.NEWS_CONFIG || {},
    isLoading: false,
    currentPage: 1,
    hasMoreNews: true,
    
    init: function() {
      this.setupInfiniteScroll();
      this.setupNewsCards();
    },
    
    setupInfiniteScroll: function() {
      var self = this;

      window.addEventListener('scroll', function() {
        if (self.isLoading || !self.hasMoreNews) return;
        
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        var windowHeight = window.innerHeight;
        var documentHeight = document.documentElement.scrollHeight;
        
        if (scrollTop + windowHeight >= documentHeight * 0.8) {
          self.loadMoreNews();
        }
      });
    },
    
    setupNewsCards: function() {
      var newsCards = document.querySelectorAll('.news-card');
      
      newsCards.forEach(function(card) {
        card.addEventListener('click', function() {
          var articleId = this.dataset.articleId;
          var title = this.querySelector('h3').textContent;
          
          if (NewsManager.config.isDevelopment) {
            alert('Переход к статье: ' + title + ' (ID: ' + articleId + ')');
          } else {
            // В продакшене здесь будет переход к реальной статье
            window.open(this.dataset.url || '#', '_blank');
          }
        });
      });
    },
    
    loadMoreNews: function() {
      if (this.isLoading || !this.hasMoreNews) return;
      
      this.isLoading = true;
      this.showLoadingSpinner();
      
      var self = this;
      
      // В режиме разработки генерируем дополнительные затычки
      if (this.config.isDevelopment) {
        setTimeout(function() {
          self.generateMockNews();
          self.hideLoadingSpinner();
          self.isLoading = false;
        }, 1500);
      } else {
        this.loadNewsFromServer();
      }
    },
    
    generateMockNews: function() {
      var mockArticles = [
        {
          id: Date.now() + Math.random(),
          title: 'Новые инвестиционные возможности',
          content: 'Анализ рынка показывает перспективные направления для инвестиций в 2025 году.',
          image: null,
          featured: false,
          date: new Date().toISOString().split('T')[0]
        },
        {
          id: Date.now() + Math.random() + 1,
          title: 'Криптовалюты: что ждет рынок?',
          content: 'Эксперты прогнозируют изменения в регулировании цифровых активов.',
          image: 'https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=400&h=300&fit=crop',
          featured: true,
          date: new Date().toISOString().split('T')[0]
        },
        {
          id: Date.now() + Math.random() + 2,
          title: 'Финансовое планирование на год',
          content: 'Рекомендации по составлению личного бюджета и достижению финансовых целей.',
          image: null,
          featured: false,
          date: new Date().toISOString().split('T')[0]
        },
        {
          id: Date.now() + Math.random() + 3,
          title: 'Налоговые изменения 2025',
          content: 'Обзор новых налоговых правил и их влияние на частных инвесторов.',
          image: null,
          featured: false,
          date: new Date().toISOString().split('T')[0]
        }
      ];
      
      var newsGrid = document.getElementById('newsGrid');
      var loadingSpinner = document.getElementById('loadingSpinner');
      
      // Добавляем новые карточки
      mockArticles.forEach(function(article) {
        var cardHtml = this.createNewsCardHtml(article);
        newsGrid.insertAdjacentHTML('beforeend', cardHtml);
      }.bind(this));
      

      this.setupNewsCards();
      
      var totalCards = document.querySelectorAll('.news-card').length;
      if (totalCards >= 20) {
        this.hasMoreNews = false;
        this.hideLoadingSpinner();
      }
    },
    
    createNewsCardHtml: function(article) {
      var imageHtml = article.image ? 
        '<img src="' + article.image + '" alt="' + article.title + '" loading="lazy">' : '';
      
      var featuredClass = article.featured ? 'featured' : '';
      
      return '<div class="news-card ' + featuredClass + '" data-article-id="' + article.id + '">' +
               imageHtml +
               '<h3>' + article.title + '</h3>' +
               '<p>' + article.content + '</p>' +
               '<div style="margin-top: 12px; font-size: 12px; color: #9aa8c7;">' +
                 article.date +
               '</div>' +
             '</div>';
    },
    
    loadNewsFromServer: function() {
      var self = this;
      var xhr = new XMLHttpRequest();
      
      xhr.open('GET', this.config.loadMoreUrl + '?page=' + (this.currentPage + 1), true);
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          self.hideLoadingSpinner();
          self.isLoading = false;
          
          if (xhr.status === 200) {
            try {
              var response = JSON.parse(xhr.responseText);
              self.displayNewsFromServer(response);
            } catch (e) {
              console.error('Ошибка парсинга ответа сервера:', e);
            }
          } else {
            console.error('Ошибка загрузки новостей:', xhr.status);
          }
        }
      };
      
      xhr.send();
    },
    
    displayNewsFromServer: function(response) {
      var newsGrid = document.getElementById('newsGrid');
      
      if (response.articles && response.articles.length > 0) {
        response.articles.forEach(function(article) {
          var cardHtml = this.createNewsCardHtml(article);
          newsGrid.insertAdjacentHTML('beforeend', cardHtml);
        }.bind(this));
        
        this.setupNewsCards();
        this.currentPage++;
        
        if (!response.hasMore) {
          this.hasMoreNews = false;
        }
      } else {
        this.hasMoreNews = false;
      }
    },
    
    showLoadingSpinner: function() {
      var spinner = document.getElementById('loadingSpinner');
      if (spinner) {
        spinner.style.display = 'flex';
      }
    },
    
    hideLoadingSpinner: function() {
      var spinner = document.getElementById('loadingSpinner');
      if (spinner) {
        spinner.style.display = 'none';
      }
    }
  };

  document.addEventListener('DOMContentLoaded', function() {
    NewsManager.init();
  });

})();

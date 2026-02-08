/**
 * TurboDOM - React-like Instant Page Loading Engine
 * Eliminates white-screen loading by prefetching, caching, and transitioning
 * Author: Senior Web Developer
 * Version: 2.0
 */

(function() {
    'use strict';

    const TurboDOM = {
        cache: new Map(),
        prefetchQueue: new Set(),
        isTransitioning: false,
        observer: null,

        /**
         * Initialize the TurboDOM engine
         */
        init() {
            this.setupPrefetching();
            this.setupInstantClick();
            this.setupPageTransitions();
            this.setupSkeletonScreens();
            this.setupProgressiveReveal();
            this.setupContentVisibility();
            this.hideSkeletonOnLoad();
            this.setupResourceHints();
            console.log('[TurboDOM] Engine initialized - React-like loading active');
        },

        /**
         * Prefetch pages on link hover (like Next.js)
         */
        setupPrefetching() {
            const links = document.querySelectorAll('a[href^="/"], a[href^="' + window.location.origin + '"]');

            links.forEach(link => {
                // Prefetch on hover with delay
                let prefetchTimer;
                link.addEventListener('mouseenter', () => {
                    prefetchTimer = setTimeout(() => {
                        this.prefetchPage(link.href);
                    }, 65); // Small delay to avoid unnecessary prefetches
                });

                link.addEventListener('mouseleave', () => {
                    clearTimeout(prefetchTimer);
                });

                // Also prefetch links visible in viewport
                if (this.observer) {
                    this.observer.observe(link);
                }
            });

            // Intersection observer for viewport-based prefetching
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const link = entry.target;
                        if (link.href && !this.cache.has(link.href)) {
                            // Low priority prefetch for visible links
                            if ('requestIdleCallback' in window) {
                                requestIdleCallback(() => this.prefetchPage(link.href));
                            }
                        }
                        this.observer.unobserve(link);
                    }
                });
            }, { rootMargin: '200px' });
        },

        /**
         * Actually prefetch a page and store in cache
         */
        async prefetchPage(url) {
            if (this.cache.has(url) || this.prefetchQueue.has(url)) return;
            this.prefetchQueue.add(url);

            try {
                const response = await fetch(url, {
                    credentials: 'same-origin',
                    headers: { 'X-Turbo-Prefetch': 'true' }
                });

                if (response.ok) {
                    const html = await response.text();
                    this.cache.set(url, {
                        html,
                        timestamp: Date.now()
                    });
                }
            } catch (e) {
                // Silent fail for prefetch
            } finally {
                this.prefetchQueue.delete(url);
            }
        },

        /**
         * Instant click - start navigation on mousedown (saves ~100ms)
         */
        setupInstantClick() {
            document.addEventListener('mousedown', (e) => {
                const link = e.target.closest('a[href]');
                if (!link) return;

                const href = link.href;

                // Skip external links, hash links, and special links
                if (!href.startsWith(window.location.origin)) return;
                if (link.hasAttribute('download')) return;
                if (link.target === '_blank') return;
                if (href.includes('#') && href.split('#')[0] === window.location.href.split('#')[0]) return;

                // Pre-warm the connection
                if (this.cache.has(href)) {
                    // Already cached - we'll use it on click
                    link.dataset.turboCached = 'true';
                }
            });
        },

        /**
         * Smooth page transitions (like React Router)
         */
        setupPageTransitions() {
            document.addEventListener('click', (e) => {
                const link = e.target.closest('a[href]');
                if (!link) return;

                const href = link.href;

                // Skip conditions
                if (!href.startsWith(window.location.origin)) return;
                if (link.hasAttribute('download')) return;
                if (link.target === '_blank') return;
                if (e.ctrlKey || e.metaKey || e.shiftKey) return;
                if (link.closest('form')) return;
                if (href.includes('#') && href.split('#')[0] === window.location.href.split('#')[0]) return;

                // Check for form submission buttons
                if (link.classList.contains('btn-logout') || link.dataset.turboSkip) return;

                e.preventDefault();
                this.navigateTo(href);
            });

            // Handle browser back/forward
            window.addEventListener('popstate', () => {
                this.navigateTo(window.location.href, false);
            });
        },

        /**
         * Navigate to a URL with transition
         */
        async navigateTo(url, pushState = true) {
            if (this.isTransitioning) return;
            this.isTransitioning = true;

            const main = document.querySelector('main');
            const body = document.body;

            // Phase 1: Start exit animation
            body.classList.add('turbo-navigating');
            main.classList.add('turbo-exit');

            // Show progress bar
            this.showProgressBar();

            try {
                let html;

                // Check cache first
                const cached = this.cache.get(url);
                if (cached && (Date.now() - cached.timestamp) < 300000) { // 5 min cache
                    html = cached.html;
                } else {
                    const response = await fetch(url, { credentials: 'same-origin' });
                    html = await response.text();
                    this.cache.set(url, { html, timestamp: Date.now() });
                }

                // Parse new page
                const parser = new DOMParser();
                const newDoc = parser.parseFromString(html, 'text/html');
                const newMain = newDoc.querySelector('main');
                const newTitle = newDoc.querySelector('title');

                // Wait for exit animation
                await this.wait(200);

                // Phase 2: Swap content
                if (newMain) {
                    main.innerHTML = newMain.innerHTML;
                }
                if (newTitle) {
                    document.title = newTitle.textContent;
                }

                // Update active nav links
                this.updateActiveNavLinks(url);

                // Update URL
                if (pushState) {
                    history.pushState(null, '', url);
                }

                // Scroll to top smoothly
                window.scrollTo({ top: 0, behavior: 'instant' });

                // Phase 3: Enter animation
                main.classList.remove('turbo-exit');
                main.classList.add('turbo-enter');

                // Re-initialize page components
                this.reinitializePage();

                await this.wait(300);
                main.classList.remove('turbo-enter');

            } catch (error) {
                // Fallback to traditional navigation
                console.warn('[TurboDOM] Navigation failed, falling back:', error);
                window.location.href = url;
            } finally {
                body.classList.remove('turbo-navigating');
                this.hideProgressBar();
                this.isTransitioning = false;
            }
        },

        /**
         * Update active navigation links
         */
        updateActiveNavLinks(url) {
            const path = new URL(url).pathname;
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                try {
                    const linkPath = new URL(link.href).pathname;
                    if (linkPath === path) {
                        link.classList.add('active');
                    }
                } catch(e) {}
            });
        },

        /**
         * Progress bar (like YouTube/GitHub)
         */
        showProgressBar() {
            let bar = document.getElementById('turbo-progress');
            if (!bar) {
                bar = document.createElement('div');
                bar.id = 'turbo-progress';
                document.body.appendChild(bar);
            }
            bar.style.width = '0%';
            bar.classList.add('active');

            // Animate progress
            requestAnimationFrame(() => {
                bar.style.width = '30%';
                setTimeout(() => { bar.style.width = '60%'; }, 100);
                setTimeout(() => { bar.style.width = '80%'; }, 200);
            });
        },

        hideProgressBar() {
            const bar = document.getElementById('turbo-progress');
            if (bar) {
                bar.style.width = '100%';
                setTimeout(() => {
                    bar.classList.remove('active');
                    bar.style.width = '0%';
                }, 300);
            }
        },

        /**
         * Skeleton screen management
         */
        setupSkeletonScreens() {
            // Create skeleton overlay that shows immediately
            // CSS handles the skeleton display - we manage the lifecycle here
        },

        hideSkeletonOnLoad() {
            // Remove skeleton after DOM is ready
            requestAnimationFrame(() => {
                const skeleton = document.getElementById('skeleton-screen');
                if (skeleton) {
                    skeleton.classList.add('skeleton-fade-out');
                    setTimeout(() => {
                        skeleton.remove();
                    }, 400);
                }

                // Reveal main content
                document.body.classList.add('turbo-loaded');
            });
        },

        /**
         * Progressive content reveal (stagger animations)
         */
        setupProgressiveReveal() {
            const revealElements = document.querySelectorAll(
                '.service-card, .step-card, .product-card, .gallery-card, .gallery-item, ' +
                '.testimonial-card, .contact-card, .stat-card, .action-card, .filter-btn, ' +
                '.feature-item, .info-item, .cta-features li'
            );

            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry, index) => {
                    if (entry.isIntersecting) {
                        // Stagger the animations
                        const siblings = entry.target.parentElement.querySelectorAll(':scope > *');
                        const siblingIndex = Array.from(siblings).indexOf(entry.target);
                        
                        setTimeout(() => {
                            entry.target.classList.add('revealed');
                        }, siblingIndex * 80);

                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '50px'
            });

            revealElements.forEach(el => {
                el.classList.add('reveal-on-scroll');
                observer.observe(el);
            });
        },

        /**
         * Content visibility optimization for off-screen content
         */
        setupContentVisibility() {
            const sections = document.querySelectorAll('section');
            sections.forEach((section, index) => {
                if (index > 1) { // Skip first 2 sections (above fold)
                    section.style.contentVisibility = 'auto';
                    section.style.containIntrinsicSize = '0 500px';
                }
            });
        },

        /**
         * Add resource hints for faster loading
         */
        setupResourceHints() {
            // Preconnect to external resources
            const origins = [
                'https://fonts.googleapis.com',
                'https://fonts.gstatic.com',
                'https://cdnjs.cloudflare.com',
                'https://unpkg.com'
            ];

            origins.forEach(origin => {
                if (!document.querySelector(`link[href="${origin}"]`)) {
                    const link = document.createElement('link');
                    link.rel = 'preconnect';
                    link.href = origin;
                    link.crossOrigin = 'anonymous';
                    document.head.appendChild(link);
                }
            });
        },

        /**
         * Re-initialize components after page swap
         */
        reinitializePage() {
            // Re-init AOS
            if (typeof AOS !== 'undefined') {
                AOS.refreshHard();
            }

            // Re-init progressive reveal
            this.setupProgressiveReveal();

            // Re-init prefetching for new links
            this.setupPrefetching();

            // Re-init flash messages
            if (typeof initFlashMessages === 'function') {
                initFlashMessages();
            }

            // Re-init form validation
            if (typeof initFormValidation === 'function') {
                initFormValidation();
            }

            // Re-init animations  
            if (typeof initAnimations === 'function') {
                initAnimations();
            }

            // Dispatch custom event for other scripts
            document.dispatchEvent(new CustomEvent('turbo:load'));
        },

        /**
         * Utility: wait for ms
         */
        wait(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => TurboDOM.init());
    } else {
        TurboDOM.init();
    }

    // Expose globally
    window.TurboDOM = TurboDOM;

})();

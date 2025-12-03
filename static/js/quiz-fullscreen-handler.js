/**
 * Quiz Fullscreen Handler
 * Automatically requests fullscreen when user clicks "Take Quiz" button
 */

(function() {
    'use strict';
    
    // Function to request fullscreen
    function requestFullscreen() {
        const element = document.documentElement;
        
        return new Promise(function(resolve, reject) {
            if (element.requestFullscreen) {
                element.requestFullscreen().then(resolve).catch(reject);
            } else if (element.webkitRequestFullscreen) {
                element.webkitRequestFullscreen();
                // Webkit doesn't return a promise, so check after a short delay
                setTimeout(function() {
                    if (document.webkitFullscreenElement) {
                        resolve();
                    } else {
                        reject(new Error('Fullscreen request failed'));
                    }
                }, 100);
            } else if (element.mozRequestFullScreen) {
                element.mozRequestFullScreen();
                setTimeout(function() {
                    if (document.mozFullScreenElement) {
                        resolve();
                    } else {
                        reject(new Error('Fullscreen request failed'));
                    }
                }, 100);
            } else if (element.msRequestFullscreen) {
                element.msRequestFullscreen();
                setTimeout(function() {
                    if (document.msFullscreenElement) {
                        resolve();
                    } else {
                        reject(new Error('Fullscreen request failed'));
                    }
                }, 100);
            } else {
                // Fullscreen API not available
                reject(new Error('Fullscreen API not supported'));
            }
        });
    }
    
    // Intercept all "Take Quiz" links
    function interceptQuizLinks() {
        // Find all links that point to take_quiz
        const quizLinks = document.querySelectorAll('a[href*="/quiz/"], a[href*="take_quiz"]');
        
        quizLinks.forEach(function(link) {
            setupQuizLink(link);
        });
    }
    
    // Also check for dynamically added links
    function observeForNewLinks() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // Check if the added node is a quiz link
                        if (node.tagName === 'A' && 
                            (node.href.includes('/quiz/') || node.href.includes('take_quiz'))) {
                            setupQuizLink(node);
                        }
                        
                        // Check for quiz links inside the added node
                        const quizLinks = node.querySelectorAll && node.querySelectorAll('a[href*="/quiz/"], a[href*="take_quiz"]');
                        if (quizLinks) {
                            quizLinks.forEach(setupQuizLink);
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // Setup a single quiz link
    function setupQuizLink(link) {
        // Check if already set up
        if (link.dataset.fullscreenHandler === 'true') {
            return;
        }
        
        link.dataset.fullscreenHandler = 'true';
        
        link.addEventListener('click', function(e) {
            const href = link.getAttribute('href');
            if (!href || (!href.includes('/quiz/') && !href.includes('take_quiz'))) {
                return;
            }
            
            e.preventDefault();
            e.stopPropagation();
            
            // Store flag BEFORE requesting fullscreen
            sessionStorage.setItem('quiz_fullscreen_requested', 'true');
            
            // Request fullscreen immediately (user gesture is still valid)
            const fullscreenPromise = requestFullscreen();
            
            // Wait for fullscreen to activate, then navigate
            fullscreenPromise.then(function() {
                // Verify fullscreen is actually active
                if (isFullscreenActive()) {
                    // Small delay to ensure fullscreen is stable
                    setTimeout(function() {
                        window.location.href = href;
                    }, 150);
                } else {
                    // Fullscreen promise resolved but not actually active - wait a bit more
                    setTimeout(function() {
                        if (isFullscreenActive()) {
                            window.location.href = href;
                        } else {
                            // Navigate anyway - quiz page will request fullscreen
                            window.location.href = href;
                        }
                    }, 200);
                }
            }).catch(function(err) {
                console.warn('Fullscreen request failed:', err);
                // Navigate anyway - quiz page will handle fullscreen request
                window.location.href = href;
            });
        });
        
        // Helper function to check if fullscreen is active
        function isFullscreenActive() {
            return !!(document.fullscreenElement || 
                     document.webkitFullscreenElement || 
                     document.mozFullScreenElement || 
                     document.msFullscreenElement);
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            interceptQuizLinks();
            observeForNewLinks();
        });
    } else {
        interceptQuizLinks();
        observeForNewLinks();
    }
})();


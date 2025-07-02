// Mobile Menu Toggle
        const hamburger = document.getElementById('hamburger');
        const sidebar = document.querySelector('.sidebar');

        // Function to toggle menu
        function toggleMenu() {
            sidebar.classList.toggle('active');
            hamburger.classList.toggle('active');
        }

        // Add click event listener
        hamburger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleMenu();
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('active') && 
                !hamburger.contains(e.target) && 
                !sidebar.contains(e.target)) {
                toggleMenu();
            }
        });

        // Close mobile menu when clicking a nav link
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', () => {
                if (sidebar.classList.contains('active')) {
                    toggleMenu();
                }
            });
        });

        // Navigation
        function navigateToSection(targetId) {
            // Update active states
            document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
            document.querySelector(`.nav-links a[href="#${targetId}"]`).classList.add('active');
            
            // Fade out all sections
            const allSections = document.querySelectorAll('.content-section');
            allSections.forEach(section => {
                if (section.classList.contains('active')) {
                    section.classList.remove('fade-in');
                    section.classList.add('fade-out');
                }
            });

            // After fade out, switch section and fade in
            setTimeout(() => {
                allSections.forEach(section => {
                    section.classList.remove('active', 'fade-in', 'fade-out');
                });
                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.classList.add('active', 'fade-in');
                }
            // Reset all tester widgets
            resetTesterWidgets();
            // Scroll to top of the page
            window.scrollTo(0, 0);
            // Only update URL hash if not overview
            if (targetId !== 'overview') {
                history.pushState(null, null, `#${targetId}`);
            } else {
                history.pushState(null, null, '/documentation');
            }
            }, 400); // match transition duration
        }

        // Function to reset tester widgets
        function resetTesterWidgets() {
            // Reset response areas and controls
            document.querySelectorAll('.response-area').forEach(area => {
                area.textContent = '';
                area.style.display = 'none';
                // Remove has-response class from parent
                const parent = area.closest('.endpoint-test');
                if (parent) parent.classList.remove('has-response');
            });
            document.querySelectorAll('.response-controls').forEach(controls => {
                controls.style.display = 'none';
            });

            // Reset language inputs and dropdowns
            ['news', 'latest'].forEach(prefix => {
                const searchInput = document.getElementById(`${prefix}LangSearch`);
                const urlLang = document.getElementById(`${prefix}UrlLang`);
                if (searchInput) searchInput.value = '';
                if (urlLang) urlLang.textContent = '';
            });

            // Reset dropdowns and their parent heights
            document.querySelectorAll('.dropdown-list').forEach(list => {
                list.classList.remove('active');
                const parent = list.closest('.endpoint-test');
                if (parent) {
                    parent.style.height = '';
                }
            });
            document.querySelectorAll('.dropdown-input').forEach(input => {
                input.classList.remove('active');
            });
        }

        // Add click handler for constructed URLs
        document.querySelectorAll('.endpoint-url').forEach(urlElement => {
            urlElement.addEventListener('click', function(e) {
                const url = this.querySelector('.url').textContent;
                // Allow copy for /languages endpoint as well as those with =
                if ((this.getAttribute('data-copyable') === 'true' && url) && (url.includes('=') ? !url.endsWith('=') : true)) {
                    const fullUrl = 'https://bbc-news-api.vercel.app' + url;
                    // Create temporary textarea
                    const textarea = document.createElement('textarea');
                    textarea.value = fullUrl;
                    document.body.appendChild(textarea);
                    textarea.select();
                    try {
                        document.execCommand('copy');
                        this.classList.add('copied');
                        let successMsg = this.querySelector('.copy-success');
                        if (!successMsg) {
                            successMsg = document.createElement('div');
                            successMsg.className = 'copy-success';
                            successMsg.innerHTML = '<i class="fas fa-check"></i> Copied!';
                            this.appendChild(successMsg);
                        }
                        setTimeout(() => {
                            this.classList.remove('copied');
                            if (successMsg) {
                                successMsg.remove();
                            }
                        }, 1500);
                    } catch (err) {
                        console.error('Failed to copy URL:', err);
                    } finally {
                        document.body.removeChild(textarea);
                    }
                }
            });
        });

        // Handle navigation clicks
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                navigateToSection(targetId);
            });
        });

        // Handle initial load and hash changes
        function handleHashChange() {
            const hash = window.location.hash.substring(1) || 'overview';
            navigateToSection(hash);
        }

        // Listen for hash changes
        window.addEventListener('hashchange', handleHashChange);

        // Handle initial load
        document.addEventListener('DOMContentLoaded', () => {
            handleHashChange();
            
            // Add click handlers for all subsection headers
            document.querySelectorAll('.sidebar-subsection-header').forEach(header => {
                header.addEventListener('click', (e) => {
                    e.stopPropagation();
                });
            });
        });

        // Helper function to show/hide loader
        function toggleLoader(buttonId, loaderId, show) {
            const button = document.getElementById(buttonId);
            const loader = document.getElementById(loaderId);
            if (show) {
                loader.style.display = 'block';
                button.disabled = true;
            } else {
                loader.style.display = 'none';
                button.disabled = false;
            }
        }

        // Helper function to update URL display
        function updateUrlDisplay(elementId, value) {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = value;
                // Update parent endpoint-url's copyable state
                const endpointUrl = element.closest('.endpoint-url');
                if (endpointUrl) {
                    endpointUrl.setAttribute('data-copyable', value ? 'true' : 'false');
                }
            }
        }

        // Custom Dropdown Functionality
        function initializeDropdown(inputId, listId, searchId, optionsId, onChange) {
            const input = document.getElementById(inputId);
            const searchInput = document.getElementById(searchId);
            const list = document.getElementById(listId);
            const options = document.getElementById(optionsId);
            let selectedValue = '';

            function toggleDropdown() {
                const isActive = list.classList.contains('active');
                if (!isActive) {
                    searchInput.focus();
                }
                list.classList.toggle('active');
                input.classList.toggle('active');

                // After opening, scroll if needed
                if (list.classList.contains('active')) {
                    setTimeout(() => {
                        const rect = list.getBoundingClientRect();
                        if (rect.bottom > window.innerHeight) {
                            list.scrollIntoView({
                                behavior: 'smooth',
                                block: 'end',
                                inline: 'nearest'
                            });
                        }
                    }, 10);
                }
            }

            input.addEventListener('click', (e) => {
                if (e.target === input || e.target === searchInput) {
                    toggleDropdown();
                }
            });

            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                const optionElements = options.getElementsByClassName('dropdown-option');
                let hasVisibleOptions = false;
                
                Array.from(optionElements).forEach(option => {
                    const text = option.textContent.toLowerCase();
                    const isVisible = text.includes(searchTerm);
                    option.style.display = isVisible ? 'flex' : 'none';
                    if (isVisible) hasVisibleOptions = true;
                });

                // Show/hide no results message
                let noResults = options.querySelector('.no-results');
                if (!hasVisibleOptions) {
                    if (!noResults) {
                        noResults = document.createElement('div');
                        noResults.className = 'no-results';
                        noResults.textContent = 'No languages found';
                        options.appendChild(noResults);
                    }
                } else if (noResults) {
                    noResults.remove();
                }
            });

            document.addEventListener('click', (e) => {
                if (!input.contains(e.target) && !list.contains(e.target)) {
                    if (list.classList.contains('active')) {
                        toggleDropdown();
                    }
                }
            });

            return {
                setOptions: (languages) => {
                    if (!Array.isArray(languages)) {
                        console.error('Languages data is not an array:', languages);
                        return;
                    }
                    options.innerHTML = languages.map(lang => `
                        <div class="dropdown-option" data-value="${lang.code}">
                            <i class="fas fa-language"></i>
                            <span>${lang.name}</span>
                        </div>
                    `).join('');

                    options.querySelectorAll('.dropdown-option').forEach(option => {
                        option.addEventListener('click', () => {
                            selectedValue = option.dataset.value;
                            searchInput.value = option.querySelector('span').textContent;
                            options.querySelectorAll('.dropdown-option').forEach(opt => 
                                opt.classList.remove('selected')
                            );
                            option.classList.add('selected');
                            // Update the endpoint URL with the selected language
                            const endpointUrl = input.closest('.endpoint-test').querySelector('.endpoint-url .url');
                            if (endpointUrl) {
                                const baseUrl = endpointUrl.textContent.split('?')[0];
                                endpointUrl.textContent = `${baseUrl}?lang=${selectedValue}`;
                                endpointUrl.closest('.endpoint-url').setAttribute('data-copyable', 'true');
                            }
                            if (onChange) onChange(selectedValue);
                            toggleDropdown();
                        });
                    });
                },
                getValue: () => selectedValue
            };
        }

        // Initialize form submissions
        document.querySelectorAll('.test-form').forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formId = form.id;
                const buttonId = formId.replace('Form', 'Button');
                const responseId = formId.replace('Form', 'Response');
                const controlsId = formId.replace('Form', 'ResponseControls');
                const viewToggleId = formId.replace('Form', 'ViewToggle');
                
                const button = document.getElementById(buttonId);
                const loader = document.getElementById(buttonId + 'Loader');
                const responseArea = document.getElementById(responseId);
                const controls = document.getElementById(controlsId);
                const viewToggle = document.getElementById(viewToggleId);
                
                if (!button || !loader || !responseArea || !controls || !viewToggle) {
                    console.error('Required elements not found:', {
                        button: buttonId,
                        loader: buttonId + 'Loader',
                        response: responseId,
                        controls: controlsId,
                        toggle: viewToggleId
                    });
                    return;
                }
                
                loader.style.display = 'block';
                button.disabled = true;
                
                try {
                    let url = '';
                    let params = {};
                    
                    switch(formId) {
                        case 'newsTestForm':
                            url = '/news';
                            const newsLang = document.getElementById('newsLangSearch').value.toLowerCase();
                            if (newsLang) {
                                params.lang = newsLang;
                            }
                            break;
                        case 'latestTestForm':
                            url = '/latest';
                            const latestLang = document.getElementById('latestLangSearch').value.toLowerCase();
                            if (latestLang) {
                                params.lang = latestLang;
                            }
                            break;
                        case 'languagesTestForm':
                            url = '/languages';
                            break;
                    }

                    const response = await fetch(url + (Object.keys(params).length ? '?' + new URLSearchParams(params) : ''));
                    const data = await response.json();
                    
                    responseArea.innerHTML = JSON.stringify(data);
                    responseArea.style.display = 'block';
                    controls.style.display = 'flex';
                    // Add has-response class to parent
                    const endpointTest = responseArea.closest('.endpoint-test');
                    if (endpointTest) endpointTest.classList.add('has-response');
                    
                    // Force a reflow to ensure the element is visible
                    responseArea.offsetHeight;
                    
                    // Smooth scroll to response area
                    responseArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    
                    // Reset view toggle
                    viewToggle.textContent = 'Switch to Tree View';
                    viewToggle.onclick = (e) => {
                        e.preventDefault();
                        if (viewToggle.textContent === 'Switch to Tree View') {
                            responseArea.innerHTML = '';
                            createTreeView(data, responseArea);
                            viewToggle.textContent = 'Switch to Raw View';
                        } else {
                            responseArea.innerHTML = JSON.stringify(data);
                            viewToggle.textContent = 'Switch to Tree View';
                        }
                        // Smooth scroll to response area after view change
                        responseArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    };
                } catch (error) {
                    console.error('Error:', error);
                    if (responseArea) {
                        responseArea.textContent = 'Error: ' + error.message;
                        responseArea.style.display = 'block';
                        controls.style.display = 'flex';
                        // Add has-response class to parent
                        const endpointTest = responseArea.closest('.endpoint-test');
                        if (endpointTest) endpointTest.classList.add('has-response');
                    }
                } finally {
                    if (button && loader) {
                        loader.style.display = 'none';
                        button.disabled = false;
                    }
                }
            });
        });

        function toggleTreeView() {
            const treeView = document.getElementById('tree-view');
            treeView.style.display = treeView.style.display === 'none' ? 'block' : 'none';
        }

        function copyCode(elementId) {
            const codeElement = document.getElementById(elementId);
            const textArea = document.createElement('textarea');
            textArea.value = codeElement.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            // Show feedback
            const button = codeElement.parentElement.parentElement.querySelector('.copy-btn');
            const originalText = button.textContent;
            button.textContent = 'Copied!';
            button.style.backgroundColor = '#28a745';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.backgroundColor = '#007bff';
            }, 2000);
        }

        // Sidebar section toggle functions
        function toggleSection(sectionId) {
            const section = document.getElementById(sectionId);
            const header = section.previousElementSibling;
            
            section.classList.toggle('active');
            header.classList.toggle('active');
        }

        function toggleSubsection(subsectionId) {
            const subsection = document.getElementById(subsectionId);
            const header = subsection.previousElementSibling;
            
            subsection.classList.toggle('active');
            header.classList.toggle('active');
        }

        // Language-specific code examples
        const codeExamples = {
            python: `import requests\n\n# Get news for Bengali\nresponse = requests.get('https://bbc-news-api.vercel.app/news?lang=bengali')\nnews = response.json()\n\n# Get latest news for Chinese\nresponse = requests.get('https://bbc-news-api.vercel.app/latest?lang=chinese')\nlatest_news = response.json()\n\n# Get list of supported languages\nresponse = requests.get('https://bbc-news-api.vercel.app/languages')\nlanguages = response.json()`,
            javascript: `// Get news for Turkish\nfetch('https://bbc-news-api.vercel.app/news?lang=turkish')\n  .then(response => response.json())\n  .then(news => console.log(news));\n\n// Get latest news for Spanish\nfetch('https://bbc-news-api.vercel.app/latest?lang=spanish')\n  .then(response => response.json())\n  .then(latest_news => console.log(latest_news));\n\n// Get list of supported languages\nfetch('https://bbc-news-api.vercel.app/languages')\n  .then(response => response.json())\n  .then(languages => console.log(languages));`,
            php: `<?php\n// Get news for Portuguese\n$news = file_get_contents('https://bbc-news-api.vercel.app/news?lang=portuguese');\n$news_data = json_decode($news, true);\n\n// Get latest news for Russian\n$latest = file_get_contents('https://bbc-news-api.vercel.app/latest?lang=russian');\n$latest_news = json_decode($latest, true);\n\n// Get list of supported languages\n$languages = file_get_contents('https://bbc-news-api.vercel.app/languages');\n$supported_languages = json_decode($languages, true);`,
            ruby: `require 'net/http'\nrequire 'json'\n\n# Get news for Japanese\nuri = URI('https://bbc-news-api.vercel.app/news?lang=japanese')\nresponse = Net::HTTP.get_response(uri)\nnews = JSON.parse(response.body)\n\n# Get latest news for Korean\nuri = URI('https://bbc-news-api.vercel.app/latest?lang=korean')\nresponse = Net::HTTP.get_response(uri)\nlatest_news = JSON.parse(response.body)\n\n# Get list of supported languages\nuri = URI('https://bbc-news-api.vercel.app/languages')\nresponse = Net::HTTP.get_response(uri)\nlanguages = JSON.parse(response.body)`,
            java: `import java.net.http.HttpClient;\nimport java.net.http.HttpRequest;\nimport java.net.http.HttpResponse;\nimport java.net.URI;\nimport org.json.JSONObject;\n\n// Get news for Hindi\nHttpClient client = HttpClient.newHttpClient();\nHttpRequest request = HttpRequest.newBuilder()\n    .uri(URI.create("https://bbc-news-api.vercel.app/news?lang=hindi"))\n    .build();\n\nHttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());\nJSONObject news = new JSONObject(response.body());`
        };

        // Language selector functionality
        function toggleLanguageDropdown() {
            const dropdown = document.getElementById('languageDropdown');
            const button = document.querySelector('.language-selector-button');
            dropdown.classList.toggle('active');
            button.classList.toggle('active');
        }

        function selectLanguage(language) {
            const dropdown = document.getElementById('languageDropdown');
            const button = document.querySelector('.language-selector-button');
            const selectedLanguage = document.getElementById('selectedLanguage');
            
            // Update selected language
            selectedLanguage.textContent = language.charAt(0).toUpperCase() + language.slice(1);
            
            // Update selected state in dropdown
            document.querySelectorAll('.language-option').forEach(option => {
                option.classList.remove('selected');
                if (option.querySelector('span').textContent.toLowerCase() === language) {
                    option.classList.add('selected');
                }
            });
            
            // Close dropdown
            dropdown.classList.remove('active');
            button.classList.remove('active');
        }

        // Function to copy code to clipboard with animation
        function copyCode() {
            const codeContent = document.getElementById('code-content').textContent;
            const copyBtn = document.getElementById('copy-btn');
            
            // Create a temporary textarea element
            const textarea = document.createElement('textarea');
            textarea.value = codeContent;
            document.body.appendChild(textarea);
            textarea.select();
            
            try {
                // Execute copy command
                document.execCommand('copy');
                
                // Update button appearance
                copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                copyBtn.classList.add('copied');
                
                // Revert back after 1.5 seconds
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
                    copyBtn.classList.remove('copied');
                }, 1500);
            } catch (err) {
                console.error('Failed to copy text: ', err);
                copyBtn.innerHTML = '<i class="fas fa-times"></i> Failed!';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
                }, 1500);
            } finally {
                // Clean up
                document.body.removeChild(textarea);
            }
        }
        // Tree View Functionality
        function createTreeView(data, parentElement) {
            if (typeof data !== 'object' || data === null) {
                const valueClass = typeof data === 'string' ? 'tree-string' :
                                typeof data === 'number' ? 'tree-number' :
                                typeof data === 'boolean' ? 'tree-boolean' : 'tree-null';
                parentElement.innerHTML = `<span class="tree-value ${valueClass}">${JSON.stringify(data)}</span>`;
                return;
            }

            const isArray = Array.isArray(data);
            const entries = isArray ? data.entries() : Object.entries(data);
            const bracketOpen = isArray ? '[' : '{';
            const bracketClose = isArray ? ']' : '}';

            // Add opening bracket
            const openBracket = document.createElement('span');
            openBracket.className = 'tree-bracket';
            openBracket.textContent = bracketOpen;
            parentElement.appendChild(openBracket);

            // Add entries
            for (const [key, value] of entries) {
                const node = document.createElement('div');
                node.className = 'tree-node';

                if (typeof value !== 'object' || value === null) {
                    // For non-object values, show them inline
                    const valueClass = typeof value === 'string' ? 'tree-string' :
                                    typeof value === 'number' ? 'tree-number' :
                                    typeof value === 'boolean' ? 'tree-boolean' : 'tree-null';
                    
                    const inlineContainer = document.createElement('div');
                    inlineContainer.className = 'tree-inline';
                    
                    const keyName = document.createElement('span');
                    keyName.className = 'tree-key-name';
                    keyName.textContent = isArray ? `[${key}]` : `"${key}"`;
                    
                    const colon = document.createElement('span');
                    colon.className = 'tree-colon';
                    colon.textContent = ':';
                    
                    const valueSpan = document.createElement('span');
                    valueSpan.className = `tree-value ${valueClass}`;
                    valueSpan.textContent = JSON.stringify(value);
                    
                    inlineContainer.appendChild(keyName);
                    inlineContainer.appendChild(colon);
                    inlineContainer.appendChild(valueSpan);
                    node.appendChild(inlineContainer);
                } else {
                    const keyElement = document.createElement('div');
                    keyElement.className = 'tree-key';

                    const toggle = document.createElement('button');
                    toggle.className = 'tree-toggle';
                    toggle.textContent = '+';
                    toggle.onclick = (e) => {
                        e.stopPropagation();
                        const content = keyElement.nextElementSibling;
                        const isExpanded = content.classList.contains('expanded');
                        content.classList.toggle('expanded');
                        toggle.textContent = isExpanded ? '+' : '-';
                    };

                    const keyName = document.createElement('span');
                    keyName.className = 'tree-key-name';
                    keyName.textContent = isArray ? `[${key}]` : `"${key}"`;

                    const colon = document.createElement('span');
                    colon.className = 'tree-colon';
                    colon.textContent = ':';

                    keyElement.appendChild(toggle);
                    keyElement.appendChild(keyName);
                    keyElement.appendChild(colon);
                    node.appendChild(keyElement);

                    const content = document.createElement('div');
                    content.className = 'tree-content';
                    createTreeView(value, content);
                    node.appendChild(content);
                }

                parentElement.appendChild(node);
            }

            // Add closing bracket
            const closeBracket = document.createElement('span');
            closeBracket.className = 'tree-bracket';
            closeBracket.textContent = bracketClose;
            parentElement.appendChild(closeBracket);
        }

        // Initialize dropdowns
        const newsDropdown = initializeDropdown('newsLangInput', 'newsLangList', 'newsLangSearch', 'newsLangOptions', (value) => {
            document.getElementById('newsLangInput').value = value;
            // Update the endpoint URL
            const endpointUrl = document.querySelector('#newsEndpoint .endpoint-url .url');
            if (endpointUrl) {
                const baseUrl = endpointUrl.textContent.split('?')[0];
                endpointUrl.textContent = `${baseUrl}?lang=${value}`;
                endpointUrl.closest('.endpoint-url').setAttribute('data-copyable', 'true');
            }
        });

        const latestDropdown = initializeDropdown('latestLangInput', 'latestLangList', 'latestLangSearch', 'latestLangOptions', (value) => {
            document.getElementById('latestLangInput').value = value;
            // Update the endpoint URL
            const endpointUrl = document.querySelector('#latestEndpoint .endpoint-url .url');
            if (endpointUrl) {
                const baseUrl = endpointUrl.textContent.split('?')[0];
                endpointUrl.textContent = `${baseUrl}?lang=${value}`;
                endpointUrl.closest('.endpoint-url').setAttribute('data-copyable', 'true');
            }
        });

        // Add loading spinner to dropdowns
        const newsLangOptions = document.getElementById('newsLangOptions');
        const latestLangOptions = document.getElementById('latestLangOptions');
        const loadingSpinner = document.createElement('div');
        loadingSpinner.className = 'loading-spinner';
        loadingSpinner.innerHTML = '<div class="spinner"></div>';
        newsLangOptions.appendChild(loadingSpinner.cloneNode(true));
        latestLangOptions.appendChild(loadingSpinner.cloneNode(true));

        // Function to adjust dropdown height
        function adjustDropdownHeight(dropdownList) {
            const list = document.getElementById(dropdownList);
            const parent = list.closest('.endpoint-test');
            const options = list.querySelector('.dropdown-options');
            if (!list || !parent || !options) return;

            const optionsHeight = Math.min(options.scrollHeight, 300) - 44;
            const currentHeight = parent.offsetHeight;
            const newHeight = currentHeight + optionsHeight;
            
            if (newHeight > currentHeight) {
                parent.style.height = `${newHeight}px`;
                const dropdownBottom = parent.getBoundingClientRect().bottom;
                const viewportHeight = window.innerHeight;
                if (dropdownBottom > viewportHeight) {
                    window.scrollTo({
                        top: window.scrollY + (dropdownBottom - viewportHeight) + 20,
                        behavior: 'smooth'
                    });
                }
            }
        }

        // Fetch languages on page load
        window.addEventListener('load', async () => {
            try {
                const response = await fetch('/languages');
                const data = await response.json();
                
                // Extract languages array from response
                const languages = data.languages || [];
                
                // Update dropdown options
                newsDropdown.setOptions(languages);
                latestDropdown.setOptions(languages);
                
                // Update Supported Languages section
                const languagesList = document.getElementById('languagesList');
                if (languagesList) {
                    languagesList.innerHTML = languages.map(lang => `
                        <div class="feature-item">
                            <i class="fa-solid fa-language"></i>
                            <h3>${lang.name}</h3>
                            <p>${lang.description}</p>
                            <code>${lang.code}</code>
                        </div>
                    `).join('');
                }

                // Remove loading spinners
                document.querySelectorAll('.loading-spinner').forEach(spinner => spinner.remove());

                // Re-trigger height adjustment for dropdowns by simulating a click
                const newsLangInput = document.getElementById('newsLangInput');
                const latestLangInput = document.getElementById('latestLangInput');
                if (newsLangInput) {
                    newsLangInput.click();
                    newsLangInput.click();
                }
                if (latestLangInput) {
                    latestLangInput.click();
                    latestLangInput.click();
                }
            } catch (error) {
                console.error('Error fetching languages:', error);
                // Show error in dropdowns
                const errorMessage = 'Error loading languages';
                newsDropdown.setOptions([{ code: '', name: errorMessage }]);
                latestDropdown.setOptions([{ code: '', name: errorMessage }]);
                // Remove loading spinners
                document.querySelectorAll('.loading-spinner').forEach(spinner => spinner.remove());
            }
        });

        // Top languages and their code examples
        const modernCodeExamples = {
            python: {
                label: 'Python',
                icon: '<i class="fab fa-python"></i>',
                code: `import requests\n\n# Get news for Bengali\nresponse = requests.get('https://bbc-news-api.vercel.app/news?lang=bengali')\nprint(response.json())\n\n# Get latest news for Hindi\nresponse = requests.get('https://bbc-news-api.vercel.app/latest?lang=hindi')\nprint(response.json())\n\n# Get list of supported languages\nresponse = requests.get('https://bbc-news-api.vercel.app/languages')\nprint(response.json())`
            },
            javascript: {
                label: 'JavaScript',
                icon: '<i class="fab fa-js"></i>',
                code: `// Get news for Bengali\nfetch('https://bbc-news-api.vercel.app/news?lang=bengali')\n  .then(res => res.json())\n  .then(data => console.log(data));\n\n// Get latest news for Hindi\nfetch('https://bbc-news-api.vercel.app/latest?lang=hindi')\n  .then(res => res.json())\n  .then(data => console.log(data));\n\n// Get list of supported languages\nfetch('https://bbc-news-api.vercel.app/languages')\n  .then(res => res.json())\n  .then(data => console.log(data));`
            },
            java: {
                label: 'Java',
                icon: '<i class="fab fa-java"></i>',
                code: `import java.net.http.HttpClient;\nimport java.net.http.HttpRequest;\nimport java.net.http.HttpResponse;\nimport java.net.URI;\n\n// Get news for Bengali\nHttpClient client = HttpClient.newHttpClient();\nHttpRequest request = HttpRequest.newBuilder()\n    .uri(URI.create("https://bbc-news-api.vercel.app/news?lang=bengali"))\n    .build();\nHttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());\nSystem.out.println(response.body());\n\n// Get latest news for Hindi\nrequest = HttpRequest.newBuilder()\n    .uri(URI.create("https://bbc-news-api.vercel.app/latest?lang=hindi"))\n    .build();\nresponse = client.send(request, HttpResponse.BodyHandlers.ofString());\nSystem.out.println(response.body());\n\n// Get list of supported languages\nrequest = HttpRequest.newBuilder()\n    .uri(URI.create("https://bbc-news-api.vercel.app/languages"))\n    .build();\nresponse = client.send(request, HttpResponse.BodyHandlers.ofString());\nSystem.out.println(response.body());`
            },
            csharp: {
                label: 'C#',
                icon: '<i class="fab fa-microsoft"></i>',
                code: `using System;\nusing System.Net.Http;\nusing System.Threading.Tasks;\n\nclass Program {\n    static async Task Main() {\n        var client = new HttpClient();\n        // Get news for Bengali\n        var news = await client.GetStringAsync("https://bbc-news-api.vercel.app/news?lang=bengali");\n        Console.WriteLine(news);\n        // Get latest news for Hindi\n        var latest = await client.GetStringAsync("https://bbc-news-api.vercel.app/latest?lang=hindi");\n        Console.WriteLine(latest);\n        // Get list of supported languages\n        var langs = await client.GetStringAsync("https://bbc-news-api.vercel.app/languages");\n        Console.WriteLine(langs);\n    }\n}`
            },
            php: {
                label: 'PHP',
                icon: '<i class="fab fa-php"></i>',
                code: `<?php\n// Get news for Bengali\n$news = file_get_contents('https://bbc-news-api.vercel.app/news?lang=bengali');\necho $news;\n\n// Get latest news for Hindi\n$latest = file_get_contents('https://bbc-news-api.vercel.app/latest?lang=hindi');\necho $latest;\n\n// Get list of supported languages\n$langs = file_get_contents('https://bbc-news-api.vercel.app/languages');\necho $langs;`
            }
        };
        // Populate dropdown
        function populateCodeLangDropdown() {
            const options = document.getElementById('codeLangOptions');
            options.innerHTML = '';
            Object.entries(modernCodeExamples).forEach(([key, val]) => {
                const div = document.createElement('div');
                div.className = 'dropdown-option';
                div.dataset.value = key;
                div.innerHTML = `${val.icon} <span>${val.label}</span>`;
                div.onclick = () => selectCodeLang(key);
                options.appendChild(div);
            });
        }
        // Dropdown logic
        function setupCodeLangDropdown() {
            const input = document.getElementById('codeLangInput');
            const list = document.getElementById('codeLangList');
            const search = document.getElementById('codeLangSearch');
            input.addEventListener('click', () => {
                list.classList.toggle('active');
            });
            document.addEventListener('click', (e) => {
                if (!input.contains(e.target) && !list.contains(e.target)) {
                    list.classList.remove('active');
                }
            });
        }
        // Select language
        function selectCodeLang(lang) {
            const search = document.getElementById('codeLangSearch');
            const codeBlock = document.getElementById('modernCodeBlock');
            const options = document.getElementById('codeLangOptions');
            // Set selected
            options.querySelectorAll('.dropdown-option').forEach(opt => opt.classList.remove('selected'));
            const selected = options.querySelector(`.dropdown-option[data-value="${lang}"]`);
            if (selected) selected.classList.add('selected');
            // Set input
            search.value = modernCodeExamples[lang].label;
            // Set code
            codeBlock.textContent = modernCodeExamples[lang].code;
            codeBlock.className = 'language-' + lang;
            // Close dropdown
            document.getElementById('codeLangList').classList.remove('active');
        }
        // Copy code
        function copyModernCode() {
            const codeBlock = document.getElementById('modernCodeBlock');
            const copyBtn = document.getElementById('modernCopyBtn');
            const text = codeBlock.textContent;
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                copyBtn.classList.add('copied');
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
                    copyBtn.classList.remove('copied');
                }, 1500);
            } catch (err) {
                copyBtn.innerHTML = '<i class="fas fa-times"></i> Failed!';
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
                }, 1500);
            } finally {
                document.body.removeChild(textarea);
            }
        }
        // Init on load
        document.addEventListener('DOMContentLoaded', () => {
            populateCodeLangDropdown();
            setupCodeLangDropdown();
            selectCodeLang('python');
        });
        // Collapsible Endpoints logic
        document.addEventListener('DOMContentLoaded', function() {
            const endpointsHeader = document.getElementById('endpointsCollapsibleHeader');
            const endpointsList = document.getElementById('endpointsCollapsibleList');
            const sidebarEndpoints = document.getElementById('sidebarEndpoints');
            let expanded = false;
            endpointsHeader.addEventListener('click', function() {
                expanded = !expanded;
                if (expanded) {
                    sidebarEndpoints.classList.add('expanded');
                } else {
                    sidebarEndpoints.classList.remove('expanded');
                }
            });
            // Optionally, expand if a sub-endpoint is active on load
            const hash = window.location.hash.substring(1);
            if (["news","latest","languages-endpoint"].includes(hash)) {
                sidebarEndpoints.classList.add('expanded');
                expanded = true;
            }
        });

        document.querySelectorAll('.endpoint-test').forEach(test => test.classList.remove('has-response'));
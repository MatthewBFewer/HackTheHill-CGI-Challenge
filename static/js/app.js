(function () {
    const translations = {
        en: {
            brand: 'Inquiry Manager',
            subtitle: 'Customer inquiry tracking',
            'nav.inquiries': 'Inquiries',
            'nav.newInquiry': 'New Inquiry',
            'home.title': 'Inquiry Triage System',
            'home.subtitle': 'Please choose an option below.',
            'customer.label': 'Customer',
            'submit.title': 'Submit an Inquiry',
            'submit.description': 'Submit a new customer inquiry for review and triage.',
            'submit.button': 'Submit an Inquiry »',
            'admin.label': 'Administrator',
            'admin.title': 'Admin Login',
            'admin.description': 'Log in to manage and review submitted inquiries.',
            'admin.button': 'Admin Login »',
            'success.title': 'Thank you!',
            'success.message': 'Your inquiry has been received successfully and will be reviewed by our team.',
            'track.label': 'Track',
            'track.title': 'My Inquiries',
            'track.description': 'Check the status of every inquiry you have submitted.',
            'track.button': 'View My Inquiries »',
            'myInquiries.title': 'My Inquiries',
            'myInquiries.subtitle': 'Track the status of every inquiry you have submitted during this site session.',
            'myInquiries.emailLabel': 'Email address',
            'myInquiries.emailPlaceholder': 'Enter the email you used to submit inquiries',
            'myInquiries.submitButton': 'Track Inquiries',
            'myInquiries.categoryLabel': 'Category:',
            'myInquiries.submittedLabel': 'Submitted:',
            'myInquiries.statusLabel': 'Status:',
            'myInquiries.viewButton': 'View',
            'myInquiries.emptyTitle': 'No inquiries found',
            'myInquiries.emptyMessage': "We couldn't find any submitted inquiries for that email address.",
            'status.pending': 'Pending',
            'status.in-progress': 'In Progress',
            'status.resolved': 'Resolved'
        },
        fr: {
            brand: 'Gestion des demandes',
            subtitle: 'Suivi des demandes clients',
            'nav.inquiries': 'Demandes',
            'nav.newInquiry': 'Nouvelle demande',
            'home.title': 'Système de tri des demandes',
            'home.subtitle': 'Choisissez une option ci-dessous.',
            'customer.label': 'Client',
            'submit.title': 'Soumettre une demande',
            'submit.description': 'Soumettre une nouvelle demande client pour examen et triage.',
            'submit.button': 'Soumettre une demande »',
            'admin.label': 'Administrateur',
            'admin.title': 'Connexion admin',
            'admin.description': 'Connectez-vous pour gérer et examiner les demandes soumises.',
            'admin.button': 'Connexion admin »',
            'success.title': 'Merci !',
            'success.message': 'Votre demande a bien été reçue et sera examinée par notre équipe.',
            'track.label': 'Suivi',
            'track.title': 'Mes demandes',
            'track.description': 'Vérifiez le statut de chaque demande que vous avez soumise.',
            'track.button': 'Voir mes demandes »',
            'myInquiries.title': 'Mes demandes',
            'myInquiries.subtitle': 'Suivez le statut de chaque demande que vous avez soumise pendant cette visite du site.',
            'myInquiries.emailLabel': 'Adresse e-mail',
            'myInquiries.emailPlaceholder': "Entrez l'e-mail que vous avez utilisé pour soumettre des demandes",
            'myInquiries.submitButton': 'Suivre les demandes',
            'myInquiries.categoryLabel': 'Catégorie :',
            'myInquiries.submittedLabel': 'Soumis :',
            'myInquiries.statusLabel': 'Statut :',
            'myInquiries.viewButton': 'Voir',
            'myInquiries.emptyTitle': 'Aucune demande trouvée',
            'myInquiries.emptyMessage': "Nous n'avons trouvé aucune demande soumise pour cette adresse e-mail.",
            'status.pending': 'En attente',
            'status.in-progress': 'En cours',
            'status.resolved': 'Résolu'
        }
    };

    function getStoredLanguage() {
        try {
            const value = localStorage.getItem('inquiryLanguage');
            return value === 'fr' ? 'fr' : 'en';
        } catch (e) {
            return 'en';
        }
    }

    function applyLanguage(lang) {
        const dict = translations[lang] || translations.en;
        const elements = document.querySelectorAll('[data-i18n]');
        const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
        const toggle = document.getElementById('languageToggle');

        elements.forEach(function (element) {
            const key = element.getAttribute('data-i18n');
            if (dict[key]) {
                element.textContent = dict[key];
            }
        });

        placeholders.forEach(function (element) {
            const key = element.getAttribute('data-i18n-placeholder');
            if (dict[key]) {
                element.setAttribute('placeholder', dict[key]);
            }
        });

        const navLinks = document.querySelectorAll('[data-i18n="nav.inquiries"], [data-i18n="nav.newInquiry"]');
        navLinks.forEach(function (element) {
            const key = element.getAttribute('data-i18n');
            if (dict[key]) {
                element.textContent = dict[key];
            }
        });

        if (toggle) {
            toggle.textContent = lang === 'en' ? 'FR' : 'EN';
            toggle.setAttribute('aria-label', lang === 'en' ? 'Switch to French' : 'Switch to English');
        }

        try {
            localStorage.setItem('inquiryLanguage', lang);
        } catch (e) {
            // ignore if storage is unavailable
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        let currentLang = getStoredLanguage();
        const toggle = document.getElementById('languageToggle');

        applyLanguage(currentLang);

        if (toggle) {
            toggle.addEventListener('click', function () {
                currentLang = currentLang === 'en' ? 'fr' : 'en';
                applyLanguage(currentLang);
            });
        }
    });
})();

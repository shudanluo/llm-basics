DOCS = [
    {
        "id": "doc1",
        "title": "Login-Probleme beheben",
        "text": """Wenn Nutzer sich nicht anmelden können, prüfen Sie zunächst die Fehlermeldung im Azure AD Sign-in Log. Der Fehlercode AADSTS50076 bedeutet, dass Multi-Faktor-Authentifizierung erforderlich ist, der Nutzer diese aber noch nicht eingerichtet hat. Leiten Sie den Nutzer zu aka.ms/mfasetup weiter. Der Fehlercode AADSTS50126 bedeutet falsches Passwort oder falscher Benutzername. Nach fünf Fehlversuchen wird das Konto für 15 Minuten gesperrt. Bei wiederholten Sperrungen sollte ein Passwort-Reset über das Admin Center durchgeführt werden. Wichtig: Prüfen Sie auch, ob der Nutzer eventuell einen Tippfehler in der E-Mail-Domain hat, das ist die häufigste Fehlerursache."""
    },
    {
        "id": "doc2",
        "title": "Abrechnung und Lizenzen",
        "text": """Die monatliche Abrechnung erfolgt immer am 1. Werktag des Folgemonats und basiert auf der tatsächlichen Nutzung im Vormonat. Business-Premium-Lizenzen kosten 22 Euro pro Nutzer und Monat, E3-Lizenzen kosten 32 Euro. Bei Lizenzänderungen während des Monats wird taggenau abgerechnet. Doppelte Abrechnungen entstehen meist, wenn ein Nutzer versehentlich zwei Lizenzen zugewiesen bekommen hat, zum Beispiel durch eine automatische Gruppenzuweisung zusätzlich zur manuellen Zuweisung. Prüfen Sie in diesem Fall im Admin Center unter 'Lizenzen > Nutzer' ob doppelte Einträge vorliegen. Rückerstattungen für fehlerhafte Abrechnungen werden innerhalb von 5 Werktagen bearbeitet."""
    },
    {
        "id": "doc3",
        "title": "SharePoint Performance-Probleme",
        "text": """Langsame Ladezeiten in SharePoint haben meist drei Hauptursachen. Erstens: zu viele Elemente in einer Liste ohne Indexierung, ab 5000 Elementen sollte ein Index angelegt werden. Zweitens: große Dateianhänge, die synchron statt asynchron geladen werden, hier hilft die Aktivierung von 'Modern Experience'. Drittens: Netzwerklatenz beim Kunden selbst, testbar über den Microsoft 365 Network Connectivity Test. Bei Praxen oder Kliniken mit älterer Netzwerk-Hardware ist meist Ursache drei relevant. Empfehlen Sie in diesem Fall einen Bandbreitentest und gegebenenfalls ein Hardware-Upgrade beim Kunden."""
    },
    {
        "id": "doc4",
        "title": "Vertragsverlängerung und Kündigung",
        "text": """Verträge verlängern sich automatisch um 12 Monate, wenn nicht spätestens 3 Monate vor Vertragsende schriftlich gekündigt wird. Bei Preiserhöhungen von mehr als 10 Prozent hat der Kunde ein Sonderkündigungsrecht innerhalb von 30 Tagen nach Ankündigung. Kunden mit Abwanderungsrisiko sollten frühzeitig vom Account Management kontaktiert werden, idealerweise 4 Monate vor Vertragsende. Bei Preisverhandlungen kann das Account Management Rabatte bis zu 15 Prozent ohne weitere Freigabe gewähren, darüber hinaus ist die Zustimmung der Geschäftsführung erforderlich."""
    },
]
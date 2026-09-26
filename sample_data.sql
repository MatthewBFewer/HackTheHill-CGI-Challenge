INSERT INTO complaints
(customer_name, customer_email, subject, description, status, category, urgency, regulatory_risk, assigned_queue)
VALUES
(
    'Jane Smith',
    'jane.smith@example.com',
    'Unexpected charge on invoice',
    'I was charged an additional service fee that was not shown when I placed my order. Please explain the charge and advise whether it can be refunded.',
    'New',
    'Billing',
    'Not assessed',
    'Not assessed',
    'Billing'
),
(
    'Michael Chen',
    'michael.chen@example.com',
    'Unable to access customer portal',
    'The customer portal rejects my password even after I reset it. I have been unable to view my account information for two days.',
    'In Progress',
    'Technical',
    'Not assessed',
    'Not assessed',
    'Technical Support'
),
(
    'Sarah Williams',
    'sarah.williams@example.com',
    'Order arrived damaged',
    'The package arrived with significant damage and the product inside is unusable. I would like a replacement or refund.',
    'New',
    'Delivery',
    'Not assessed',
    'Not assessed',
    'Customer Service'
),
(
    'David Brown',
    'david.brown@example.com',
    'Question about account closure',
    'I requested that my account be closed last week but continue to receive account-related messages. Please confirm the status of my request.',
    'Resolved',
    'Service',
    'Not assessed',
    'Not assessed',
    'Customer Service'
),
(
    'Emily Johnson',
    'emily.johnson@example.com',
    'Product information appears incorrect',
    'The specifications displayed on the product page do not appear to match the item I received. Please review the listing and let me know what information is correct.',
    'New',
    'Product',
    'Not assessed',
    'Not assessed',
    'Product Support'
);

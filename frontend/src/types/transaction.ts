/**
 * Transaction input data structure
 * All fields required for fraud detection analysis
 */
export interface Transaction {
    trans_date_trans_time: string;
    cc_num: number;
    merchant: string;
    category: string;
    amt: number;
    first: string;
    last: string;
    gender: string;
    street: string;
    city: string;
    state: string;
    zip: string;
    lat: number;
    long: number;
    city_pop: number;
    job: string;
    dob: string;
    trans_num: string;
    unix_time: number;
    merch_lat: number;
    merch_long: number;
}

/**
 * Form field configuration for rendering
 */
export interface FormField {
    name: keyof Transaction;
    label: string;
    type: 'text' | 'number' | 'datetime-local' | 'select';
    placeholder?: string;
    options?: string[]; // For select fields
    step?: string; // For number fields
}

export const FORM_FIELDS: FormField[] = [
    // Personal Info
    { name: 'first', label: 'First Name', type: 'text', placeholder: 'John' },
    { name: 'last', label: 'Last Name', type: 'text', placeholder: 'Doe' },
    { name: 'gender', label: 'Gender', type: 'select', options: ['M', 'F'] },
    { name: 'dob', label: 'Date of Birth', type: 'text', placeholder: 'YYYY-MM-DD' },
    { name: 'job', label: 'Job', type: 'text', placeholder: 'Engineer' },
    { name: 'city_pop', label: 'City Population', type: 'number' },

    // Transaction
    { name: 'amt', label: 'Amount', type: 'number', step: '0.01' },
    { name: 'merchant', label: 'Merchant', type: 'text', placeholder: 'fraud_MerchantName' },
    { name: 'category', label: 'Category', type: 'text', placeholder: 'misc_net' },
    { name: 'trans_date_trans_time', label: 'Date/Time', type: 'text', placeholder: 'YYYY-MM-DD HH:MM:SS' },
    { name: 'cc_num', label: 'Credit Card Number', type: 'number' },

    // Location
    { name: 'street', label: 'Street', type: 'text' },
    { name: 'city', label: 'City', type: 'text' },
    { name: 'state', label: 'State', type: 'text' },
    { name: 'zip', label: 'Zip Code', type: 'text' },
    { name: 'lat', label: 'Latitude', type: 'number', step: '0.0001' },
    { name: 'long', label: 'Longitude', type: 'number', step: '0.0001' },

    // Merchant Location
    { name: 'merch_lat', label: 'Merchant Lat', type: 'number', step: '0.0001' },
    { name: 'merch_long', label: 'Merchant Long', type: 'number', step: '0.0001' },

    // Meta
    { name: 'trans_num', label: 'Transaction Num', type: 'text' },
    { name: 'unix_time', label: 'Unix Time', type: 'number' },
];

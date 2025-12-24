import { useState, useCallback } from 'react';
import { Transaction } from '@/types/transaction';

/**
 * Custom hook for transaction form state management
 * 
 * Features:
 * - Form state management
 * - Validation
 * - Random transaction generation from example data
 * - Field updates
 */
export function useTransactionForm() {
    const [formData, setFormData] = useState<Transaction>(getEmptyTransaction());
    const [errors, setErrors] = useState<Partial<Record<keyof Transaction, string>>>({});

    /**
     * Generate random transaction from example-data.json
     */
    const generateRandomTransaction = useCallback(async () => {
        try {
            const response = await fetch('/example-data.json');
            const examples: Transaction[] = await response.json();

            // Pick random transaction
            const randomIndex = Math.floor(Math.random() * examples.length);
            const randomTx = examples[randomIndex];

            setFormData(randomTx);
            setErrors({});
        } catch (error) {
            console.error('Failed to load example data:', error);
        }
    }, []);

    /**
     * Update single field
     */
    const updateField = useCallback((field: keyof Transaction, value: any) => {
        // Handle number conversion
        let parsedValue = value;
        if (typeof value === 'string' && !isNaN(Number(value)) && value.trim() !== '') {
            // Only parse if the field type is number-ish. 
            // For simplicity, we trust the input type, but React input[type=number] gives strings.
            // We'll parse in the component or here. Let's keep it flexible.
        }

        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear error for this field
        setErrors(prev => {
            const newErrors = { ...prev };
            delete newErrors[field];
            return newErrors;
        });
    }, []);

    /**
     * Validate form data
     */
    const validate = useCallback((): boolean => {
        const newErrors: Partial<Record<keyof Transaction, string>> = {};

        // Required fields validation
        if (!formData.amt || Number(formData.amt) <= 0) {
            newErrors.amt = 'Amount must be greater than 0';
        }
        if (!formData.merchant) {
            newErrors.merchant = 'Merchant is required';
        }
        if (!formData.cc_num) {
            newErrors.cc_num = 'Credit Card Number is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    }, [formData]);

    /**
     * Reset form to empty state
     */
    const resetForm = useCallback(() => {
        setFormData(getEmptyTransaction());
        setErrors({});
    }, []);

    return {
        formData,
        errors,
        updateField,
        generateRandomTransaction,
        validate,
        resetForm
    };
}

/**
 * Get empty transaction with default values
 */
function getEmptyTransaction(): Transaction {
    return {
        trans_date_trans_time: '',
        cc_num: 0,
        merchant: '',
        category: '',
        amt: 0,
        first: '',
        last: '',
        gender: 'M',
        street: '',
        city: '',
        state: '',
        zip: '',
        lat: 0,
        long: 0,
        city_pop: 0,
        job: '',
        dob: '',
        trans_num: '',
        unix_time: 0,
        merch_lat: 0,
        merch_long: 0
    };
}

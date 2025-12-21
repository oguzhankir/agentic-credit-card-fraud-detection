import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { TransactionInput, TransactionCategory } from "@/lib/types";
import { cn } from "@/lib/utils";

interface TransactionFormProps {
    onSubmit: (data: TransactionInput) => void;
    isLoading: boolean;
}

const CATEGORIES: TransactionCategory[] = [
    'grocery_pos', 'gas_transport', 'shopping_net', 'shopping_pos',
    'food_dining', 'entertainment', 'health_fitness', 'travel',
    'personal_care', 'kids_pets', 'home', 'misc_net', 'misc_pos'
];

export const TransactionForm: React.FC<TransactionFormProps> = ({ onSubmit, isLoading }) => {
    const [formData, setFormData] = useState<Partial<TransactionInput>>({
        amount: 0,
        merchant: '',
        category: 'misc_pos',
        location: { lat: 0, long: 0, distance_from_home: 0 },
        customer_id: 'cust_001',
        time: new Date().toISOString().slice(0, 16) // datetime-local format
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        if (name.includes('.')) {
            const [parent, child] = name.split('.');
            setFormData(prev => ({
                ...prev,
                [parent]: {
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    ...(prev as any)[parent],
                    [child]: child === 'distance_from_home' ? parseFloat(value) : value
                }
            }));
        } else {
            setFormData(prev => ({
                ...prev,
                [name]: name === 'amount' ? parseFloat(value) : value
            }));
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (formData.amount && formData.merchant && formData.location) {
            // Add Customer History Logic Mock
            const fullData: TransactionInput = {
                ...formData as TransactionInput,
                customer_history: {
                    avg_amount: 100,
                    std_amount: 20,
                    usual_hours: [9, 10, 11, 12, 18, 19],
                    transaction_count: 50
                }
            };
            onSubmit(fullData);
        }
    };

    const loadDemo = (type: 'high' | 'low') => {
        if (type === 'high') {
            setFormData({
                amount: 2500,
                merchant: "Electronics Store",
                category: "shopping_pos",
                time: new Date().toISOString().slice(0, 16),
                location: { lat: 40, long: -70, distance_from_home: 150 },
                customer_id: "cust_demo_high"
            });
        } else {
            setFormData({
                amount: 45.50,
                merchant: "Local Grocery",
                category: "grocery_pos",
                time: new Date().toISOString().slice(0, 16),
                location: { lat: 40, long: -70, distance_from_home: 2 },
                customer_id: "cust_demo_low"
            });
        }
    };

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Transaction Details</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Amount ($)</label>
                            <input
                                type="number" step="0.01" name="amount"
                                value={formData.amount} onChange={handleChange}
                                className="w-full p-2 border rounded-md" required
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Time</label>
                            <input
                                type="datetime-local" name="time"
                                value={formData.time} onChange={handleChange}
                                className="w-full p-2 border rounded-md" required
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Merchant</label>
                        <input
                            type="text" name="merchant"
                            value={formData.merchant} onChange={handleChange}
                            className="w-full p-2 border rounded-md" required
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Category</label>
                        <select
                            name="category"
                            value={formData.category} onChange={handleChange}
                            className="w-full p-2 border rounded-md capitalize"
                        >
                            {CATEGORIES.map(c => (
                                <option key={c} value={c}>{c.replace('_', ' ')}</option>
                            ))}
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Distance from Home (km)</label>
                        <input
                            type="number" name="location.distance_from_home"
                            value={formData.location?.distance_from_home || ''} onChange={handleChange}
                            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" required
                        />
                    </div>

                    <div className="pt-4 flex gap-2">
                        <button
                            type="button" onClick={() => loadDemo('low')}
                            className="text-xs px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full hover:bg-emerald-200 font-medium transition-colors"
                        >
                            Load Low Risk Scenario
                        </button>
                        <button
                            type="button" onClick={() => loadDemo('high')}
                            className="text-xs px-3 py-1 bg-rose-100 text-rose-700 rounded-full hover:bg-rose-200 font-medium transition-colors"
                        >
                            Load High Risk Scenario
                        </button>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className={cn(
                            "w-full py-2.5 px-4 rounded-md text-white font-semibold shadow-sm transition-all duration-200",
                            isLoading
                                ? "bg-slate-400 cursor-not-allowed"
                                : "bg-blue-600 hover:bg-blue-700 hover:shadow-md active:transform active:scale-[0.98]"
                        )}
                    >
                        {isLoading ? (
                            <span className="flex items-center justify-center gap-2">
                                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Running Analysis...
                            </span>
                        ) : "Analyze Transaction"}
                    </button>
                </form>
            </CardContent>
        </Card>
    );
};

import React, { useState } from 'react';
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
        location: { lat: 40.7128, long: -74.006, distance_from_home: 0, state: 'NY' },
        customer_id: 'cust_001',
        time: new Date().toISOString().slice(0, 16)
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        if (name.includes('.')) {
            const [parent, child] = name.split('.');
            setFormData(prev => ({
                ...prev,
                [parent]: {
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
        if (formData.amount !== undefined && formData.merchant && formData.location) {
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
            // High Risk - Fraud Example Provided by User
            setFormData({
                amount: 24.84,
                merchant: "fraud_Hamill-D'Amore",
                category: "health_fitness",
                time: "2020-06-21T22:06",
                location: { lat: 31.8599, long: -102.7413, distance_from_home: 2500, state: 'TX', city: "Notrees" },
                customer_id: "cust_demo_high",

                // Raw Data Fields
                cc_num: "3560725013359375",
                first: "Brooke",
                last: "Smith",
                gender: "F",
                street: "63542 Luna Brook Apt. 012",
                zip: 79759,
                city_pop: 23,
                city: "Notrees",
                state: "TX",
                job: "Cytogeneticist",
                dob: "1969-09-15",
                trans_num: "16bf2e46c54369a8eab2214649506425",
                unix_time: 1371852399,
                merch_lat: 32.575873,
                merch_long: -102.60429
            } as TransactionInput);
        } else {
            // Low Risk - Legit Example Provided by User
            setFormData({
                amount: 2.86,
                merchant: "fraud_Kirlin and Sons",
                category: "personal_care",
                time: "2020-06-21T12:14",
                location: { lat: 33.9659, long: -80.9355, distance_from_home: 1.2, state: 'SC', city: "Columbia" },
                customer_id: "cust_demo_low",

                // Raw Data Fields
                cc_num: "2291163933867244",
                first: "Jeff",
                last: "Elliott",
                gender: "M",
                street: "351 Darlene Green",
                city: "Columbia",
                state: "SC",
                zip: 29209,
                city_pop: 333497,
                job: "Mechanical engineer",
                dob: "1968-03-19",
                trans_num: "2da90c7d74bd46a0caf3777415b3ebd3",
                unix_time: 1371816865,
                merch_lat: 33.986391,
                merch_long: -81.200714
            } as TransactionInput);
        }
    };

    const inputClasses = "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-gray-600 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50 outline-none transition-all";

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                    <label className="text-[10px] font-black uppercase tracking-widest text-gray-500 ml-1">Amount ($)</label>
                    <input
                        type="number" step="0.01" name="amount"
                        value={formData.amount} onChange={handleChange}
                        className={inputClasses} required
                    />
                </div>
                <div className="space-y-1.5">
                    <label className="text-[10px] font-black uppercase tracking-widest text-gray-500 ml-1">Timestamp</label>
                    <input
                        type="datetime-local" name="time"
                        value={formData.time} onChange={handleChange}
                        className={inputClasses} required
                    />
                </div>
            </div>

            <div className="space-y-1.5">
                <label className="text-[10px] font-black uppercase tracking-widest text-gray-500 ml-1">Merchant Identity</label>
                <input
                    type="text" name="merchant" placeholder="e.g. Amazon, Starbucks"
                    value={formData.merchant} onChange={handleChange}
                    className={inputClasses} required
                />
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                    <label className="text-[10px] font-black uppercase tracking-widest text-gray-500 ml-1">Category</label>
                    <select
                        name="category"
                        value={formData.category} onChange={handleChange}
                        className={cn(inputClasses, "appearance-none")}
                    >
                        {CATEGORIES.map(c => (
                            <option key={c} value={c} className="bg-slate-900">{c.replace('_', ' ')}</option>
                        ))}
                    </select>
                </div>
                <div className="space-y-1.5">
                    <label className="text-[10px] font-black uppercase tracking-widest text-gray-500 ml-1">Distance (km)</label>
                    <input
                        type="number" name="location.distance_from_home"
                        value={formData.location?.distance_from_home || ''} onChange={handleChange}
                        className={inputClasses} required
                    />
                </div>
            </div>

            {/* Raw Data Validation Section */}
            <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                <details className="group">
                    <summary className="flex items-center justify-between cursor-pointer text-xs font-bold text-gray-400 group-hover:text-blue-400 transition-colors list-none">
                        <span>RAW DATA INPUTS (Advanced)</span>
                        <span className="text-[10px] border border-white/10 px-2 py-0.5 rounded-full group-open:bg-blue-500/10 group-open:text-blue-400">
                            {formData.first ? 'Active' : 'Empty'}
                        </span>
                    </summary>
                    <div className="mt-4 grid grid-cols-2 gap-3 pb-2">
                        <div className="col-span-2">
                            <label className="text-[9px] uppercase tracking-widest text-gray-600">Full Name</label>
                            <div className="flex gap-2">
                                <input type="text" name="first" value={formData.first || ''} onChange={handleChange} placeholder="First" className={cn(inputClasses, 'text-xs')} />
                                <input type="text" name="last" value={formData.last || ''} onChange={handleChange} placeholder="Last" className={cn(inputClasses, 'text-xs')} />
                            </div>
                        </div>
                        <div>
                            <label className="text-[9px] uppercase tracking-widest text-gray-600">Job</label>
                            <input type="text" name="job" value={formData.job || ''} onChange={handleChange} className={cn(inputClasses, 'text-xs')} />
                        </div>
                        <div>
                            <label className="text-[9px] uppercase tracking-widest text-gray-600">City / State / Pop</label>
                            <div className="flex gap-1">
                                <input type="text" name="location.city" value={formData.location?.city || formData.city || ''} onChange={handleChange} placeholder="City" className={cn(inputClasses, 'text-xs')} />
                                <input type="text" name="location.state" value={formData.location?.state || formData.state || ''} onChange={handleChange} placeholder="ST" className={cn(inputClasses, 'text-xs w-12')} />
                                <input type="number" name="city_pop" value={formData.city_pop || ''} onChange={handleChange} placeholder="Pop" className={cn(inputClasses, 'text-xs w-16')} />
                            </div>
                        </div>
                        <div>
                            <label className="text-[9px] uppercase tracking-widest text-gray-600">CC Num</label>
                            <input type="text" name="cc_num" value={formData.cc_num || ''} onChange={handleChange} className={cn(inputClasses, 'text-xs font-mono')} />
                        </div>
                        <div>
                            <label className="text-[9px] uppercase tracking-widest text-gray-600">DOB</label>
                            <input type="date" name="dob" value={formData.dob || ''} onChange={handleChange} className={cn(inputClasses, 'text-xs')} />
                        </div>
                    </div>
                </details>
            </div>

            <div className="pt-2 flex flex-col gap-3">
                <div className="flex gap-2">
                    <button
                        type="button" onClick={() => loadDemo('low')}
                        className="flex-1 text-[10px] font-black uppercase tracking-tighter py-2 rounded-xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors"
                    >
                        Simulate Low Risk
                    </button>
                    <button
                        type="button" onClick={() => loadDemo('high')}
                        className="flex-1 text-[10px] font-black uppercase tracking-tighter py-2 rounded-xl bg-rose-500/10 text-rose-500 border border-rose-500/20 hover:bg-rose-500/20 transition-colors"
                    >
                        Simulate High Risk (Real Fraud)
                    </button>
                </div>

                <button
                    type="submit"
                    disabled={isLoading}
                    className={cn(
                        "w-full py-4 rounded-xl text-sm font-black uppercase tracking-widest text-white shadow-2xl transition-all duration-300",
                        isLoading
                            ? "bg-gray-800 cursor-not-allowed opacity-50"
                            : "bg-blue-600 hover:bg-blue-500 hover:shadow-blue-500/25 active:scale-[0.98]"
                    )}
                >
                    {isLoading ? (
                        <span className="flex items-center justify-center gap-3">
                            <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                            Analyzing Vector...
                        </span>
                    ) : "Execute Analysis"}
                </button>
            </div>
        </form>
    );
};

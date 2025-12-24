import { Transaction, FORM_FIELDS } from '@/types/transaction';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2, Shuffle } from 'lucide-react';

interface Props {
    formData: Transaction;
    errors: Partial<Record<keyof Transaction, string>>;
    isAnalyzing: boolean;
    onFieldChange: (field: keyof Transaction, value: any) => void;
    onGenerate: () => void;
    onSubmit: () => void;
    onReset: () => void;
}

export function TransactionForm({
    formData,
    errors,
    isAnalyzing,
    onFieldChange,
    onGenerate,
    onSubmit,
    onReset
}: Props) {

    const renderField = (field: typeof FORM_FIELDS[0]) => {
        return (
            <div key={field.name} className="space-y-2">
                <Label htmlFor={field.name}>{field.label}</Label>

                {field.type === 'select' ? (
                    <Select
                        value={String(formData[field.name])}
                        onValueChange={(val) => onFieldChange(field.name, val)}
                        disabled={isAnalyzing}
                    >
                        <SelectTrigger id={field.name} className={errors[field.name] ? "border-red-500" : ""}>
                            <SelectValue placeholder="Select..." />
                        </SelectTrigger>
                        <SelectContent>
                            {field.options?.map(opt => (
                                <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                ) : (
                    <Input
                        id={field.name}
                        type={field.type}
                        placeholder={field.placeholder}
                        value={formData[field.name] || ''}
                        onChange={(e) => onFieldChange(field.name, e.target.value)}
                        disabled={isAnalyzing}
                        step={field.step}
                        className={errors[field.name] ? "border-red-500" : ""}
                    />
                )}

                {errors[field.name] && (
                    <p className="text-xs text-red-500">{errors[field.name]}</p>
                )}
            </div>
        );
    };

    return (
        <Card className="w-full">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                <div>
                    <CardTitle>Transaction Details</CardTitle>
                    <CardDescription>Enter details or generate random data</CardDescription>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={onGenerate}
                    disabled={isAnalyzing}
                    className="flex gap-2"
                >
                    <Shuffle className="w-4 h-4" />
                    Random
                </Button>
            </CardHeader>

            <CardContent className="space-y-6">
                <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }}>
                    {/* Personal Info */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider border-b pb-2">Customer Info</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {FORM_FIELDS.slice(0, 6).map(renderField)}
                        </div>
                    </div>

                    {/* Transaction Info */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider border-b pb-2">Payment Details</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {FORM_FIELDS.slice(6, 11).map(renderField)}
                        </div>
                    </div>

                    {/* Location Info */}
                    <div className="space-y-4">
                        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider border-b pb-2">Location Data</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {FORM_FIELDS.slice(11, 20).map(renderField)}
                        </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex gap-3 pt-4">
                        <Button
                            type="submit"
                            className="flex-1"
                            disabled={isAnalyzing}
                            size="lg"
                        >
                            {isAnalyzing ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Analyzing...
                                </>
                            ) : (
                                'Analyze Transaction'
                            )}
                        </Button>
                        <Button
                            type="button"
                            variant="secondary"
                            onClick={onReset}
                            disabled={isAnalyzing}
                            size="lg"
                        >
                            Reset
                        </Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    );
}

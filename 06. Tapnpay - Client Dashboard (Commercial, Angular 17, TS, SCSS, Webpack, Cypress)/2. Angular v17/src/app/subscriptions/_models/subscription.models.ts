export interface SubscriptionModels {
}

export enum SubscriptionStatus {
    ACTIVE = "ACTIVE",
    EXPIRED = "EXPIRED",
    ACTIVE_UNTIL_EXPIRATION = "ACTIVE_UNTIL_EXPIRATION",
    NO_SUBSCRIPTION = "NO_SUBSCRIPTION",
    NEXT_TO_ACTIVE = "NEXT_TO_ACTIVE",
}

export enum SubscriptionType {
    NO_PAY_CAR = "NO_PAY_CAR",
    PAY_PER_CAR = "PAY_PER_CAR",
    PAY_PER_BUNDLE = "PAY_PER_BUNDLE",
}

export type SubscriptionUpdateType =
    'NEW'
    | 'UPGRADE'
    | 'DOWNGRADE'
    | 'DOWNGRADE_WITH_PAYMENT'
    | 'NO_CHANGE'
    | 'NO_CHANGE_WITH_PAYMENT';

export enum SubscriptionUpdateTypeEnum {
    NEW = 'NEW',
    UPGRADE = 'UPGRADE',
    DOWNGRADE = 'DOWNGRADE',
    DOWNGRADE_WITH_PAYMENT = 'DOWNGRADE_WITH_PAYMENT',
    NO_CHANGE = 'NO_CHANGE',
    NO_CHANGE_WITH_PAYMENT = 'NO_CHANGE_WITH_PAYMENT'
}

export interface SetSubscriptionPlanOptions {
    subscription_plan_id: string;
    verification_code: string;
    payment_method_type: string;
    payment_method_id: string;
    return_url: string;
    cancel_url: string;
}

export interface SetSubscriptionPaymentIntent {
    amount: number;
    currency: string;
    id: string;
    client_secret: string;
    approve_payment_url: string;
}

export interface SetSubscriptionPlanResponse {
    subscription_id: string;
    payment_intent: SetSubscriptionPaymentIntent;
    transaction_id: string;
    payment_complete: boolean;
}

export interface CompareSubscriptionPlanResponse {
    current_plan_id: string
    current_max_lp: number;
    current_active_until: Date;
    next_max_lp: number;
    billing_amount: number;
    next_plan_id: string
    next_billing_amount: number;
    next_billing_date: Date;
    update_type: SubscriptionUpdateType;
}


export interface SubscriptionListItem {
    id: string;
    price: number;
    type: SubscriptionType;
    duration: {
        type: string;
        value: Date;
    };
    discount: number,
    max_license_plates: number;
}

export interface AllSubscriptionPlansResponse {
    plans: SubscriptionListItem[];
}

export interface CurrentSubscriptionResponse {
    status: SubscriptionStatus;
    type: SubscriptionType;
    price: number;
    duration: {
        type: string;
        value: number;
    };
    subscription_plan_id: string;
    next_subscription_plan_id: string;
    next_billing_date: Date;
    "next_billing_amount": number;
    "next_max_lp": number;
    max_lp: number;
    active_until_date: Date;
    expired_date: string;
}

export interface SubscriptionToShow {
    status: SubscriptionStatus,
    next_billing_date: Date,
    price: number,
    max_lp: number
    active_until_date?: Date,
    expired_date?: Date
}

export interface CheckSubscriptionActionsResponse {
    add_license_plate: boolean
}

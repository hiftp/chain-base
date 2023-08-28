-- disable hitpay payment provider
UPDATE payment_provider
   SET hitpay_api_key = NULL,
       hitpay_api_salty = NULL;

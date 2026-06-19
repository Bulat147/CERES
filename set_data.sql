BEGIN;

DELETE FROM hardware_events;
DELETE FROM cell_events;
DELETE FROM payments;
DELETE FROM rentals;
DELETE FROM payment_methods;
DELETE FROM locker_cells;
DELETE FROM locker_stations;
DELETE FROM users;

COMMIT;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO users (
    id,
    phone,
    email,
    password_hash,
    full_name,
    status,
    created_at
)
SELECT
    gen_random_uuid(),
    '+79' || LPAD((floor(random()*1000000000))::text, 10, '0'),
    'user' || g || '@mail.ru',
    '$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5JmYHxGblMb6XHKPYBxqFzGK',
    full_name,
    status,
    NOW() - (random() * interval '180 days')
FROM (
    SELECT
        generate_series(1,15) g,
        unnest(ARRAY[
            'Иванов Иван Сергеевич',
            'Петров Петр Андреевич',
            'Сидоров Алексей Игоревич',
            'Кузнецов Дмитрий Олегович',
            'Смирнова Анна Викторовна',
            'Попова Мария Алексеевна',
            'Васильев Максим Романович',
            'Новикова Екатерина Павловна',
            'Морозов Артем Николаевич',
            'Федорова Ольга Сергеевна',
            'Белов Кирилл Андреевич',
            'Крылова Дарья Игоревна',
            'Орлов Денис Викторович',
            'Тихонова Светлана Юрьевна',
            'Семенов Андрей Петрович'
        ]) full_name,
        unnest(ARRAY[
            'active','active','active','active','active',
            'active','active','active','active','active',
            'active','active','blocked','active','active'
        ]) status
) t;


INSERT INTO locker_stations (
    id,
    title,
    address,
    latitude,
    longitude,
    status,
    created_at
)
VALUES
(gen_random_uuid(),'ТЦ Авиапарк','Москва, Ходынский бульвар, 4',55.7901,37.5317,'ACTIVE',NOW()),
(gen_random_uuid(),'ТРЦ Европейский','Москва, площадь Киевского вокзала, 2',55.7448,37.5654,'ACTIVE',NOW()),
(gen_random_uuid(),'ТЦ Метрополис','Москва, Ленинградское шоссе, 16А',55.8529,37.4792,'ACTIVE',NOW()),
(gen_random_uuid(),'ТЦ ГУМ','Москва, Красная площадь, 3',55.7545,37.6212,'ACTIVE',NOW()),
(gen_random_uuid(),'ТРЦ Ривьера','Москва, Автозаводская, 18',55.7051,37.6431,'ACTIVE',NOW()),
(gen_random_uuid(),'ТЦ Атриум','Москва, Земляной Вал, 33',55.7574,37.6591,'ACTIVE',NOW()),
(gen_random_uuid(),'ТРЦ Колумбус','Москва, Кировоградская, 13А',55.6118,37.6065,'ACTIVE',NOW()),
(gen_random_uuid(),'ТРЦ Саларис','Москва, Киевское шоссе',55.6223,37.4246,'ACTIVE',NOW()),
(gen_random_uuid(),'ТЦ Мега Химки','Химки, микрорайон ИКЕА',55.9114,37.3969,'ACTIVE',NOW()),
(gen_random_uuid(),'ТРЦ Щука','Москва, Щукинская, 42',55.8098,37.4641,'MAINTENANCE',NOW());


INSERT INTO locker_cells (
    id,
    station_id,
    number,
    title,
    size,
    hourly_price,
    status,
    hardware_id,
    created_at
)
SELECT
    gen_random_uuid(),
    s.id,
    n,
    'Ячейка ' || n,
    CASE
        WHEN n <= 8 THEN 'SMALL'
        WHEN n <= 15 THEN 'MEDIUM'
        ELSE 'LARGE'
    END,
    CASE
        WHEN n <= 8 THEN 50
        WHEN n <= 15 THEN 80
        ELSE 120
    END,
    CASE
        WHEN random() < 0.6 THEN 'AVAILABLE'
        WHEN random() < 0.8 THEN 'ACTIVE'
        WHEN random() < 0.9 THEN 'RESERVED'
        WHEN random() < 0.95 THEN 'BLOCKED'
        ELSE 'OFFLINE'
    END,
    'HW-' || substring(s.id::text,1,8) || '-' || n,
    NOW()
FROM locker_stations s
CROSS JOIN generate_series(1,20) n;

INSERT INTO payment_methods (
    id,
    user_id,
    provider,
    masked_pan,
    token,
    is_verified,
    created_at
)
SELECT
    gen_random_uuid(),
    u.id,
    CASE
        WHEN random() < 0.5 THEN 'YooKassa'
        ELSE 'Sberbank'
    END,
    '**** **** **** ' || LPAD((floor(random()*9999)+1)::text,4,'0'),
    'tok_' || substr(md5(random()::text),1,20),
    TRUE,
    NOW() - (random() * interval '90 days')
FROM users u;


INSERT INTO rentals (
    id,
    user_id,
    cell_id,
    started_at,
    ended_at,
    status,
    price_per_hour,
    final_amount,
    payment_status,
    payment_method_id,
    opened_at,
    closed_at,
    created_at
)
SELECT
    gen_random_uuid(),
    rd.user_id,
    rd.cell_id,
    rd.started_at,
    rd.ended_at,
    rd.status,
    rd.price_per_hour,
    rd.final_amount,
    rd.payment_status,
    CASE
        WHEN rd.status IN ('ACTIVE', 'WAITING_CLOSE')
        THEN (SELECT pm.id FROM payment_methods pm WHERE pm.user_id = rd.user_id ORDER BY random() LIMIT 1)
        ELSE NULL
    END,
    rd.opened_at,
    rd.closed_at,
    rd.created_at
FROM (
    SELECT
        u.id AS user_id,
        (SELECT c.id FROM locker_cells c ORDER BY random() LIMIT 1) AS cell_id,
        NOW() - (random() * interval '30 days') AS started_at,
        NOW() - (random() * interval '10 days') AS ended_at,
        CASE
            WHEN random() < 0.5 THEN 'COMPLETED'
            WHEN random() < 0.7 THEN 'ACTIVE'
            WHEN random() < 0.85 THEN 'WAITING_CLOSE'
            ELSE 'CANCELLED'
        END AS status,
        (ARRAY[50,80,120])[floor(random()*3+1)] AS price_per_hour,
        round((random()*1000 + 100)::numeric, 2) AS final_amount,
        CASE
            WHEN random() < 0.8 THEN 'PAID'
            WHEN random() < 0.9 THEN 'PENDING'
            ELSE 'FAILED'
        END AS payment_status,
        NOW() - (random() * interval '30 days') AS opened_at,
        NOW() - (random() * interval '5 days') AS closed_at,
        NOW() - (random() * interval '30 days') AS created_at
    FROM generate_series(1,100) g
    JOIN LATERAL (SELECT id FROM users ORDER BY random() LIMIT 1) u ON true
) rd;


INSERT INTO payments (
    id,
    rental_id,
    user_id,
    payment_method_id,
    amount,
    currency,
    status,
    provider,
    provider_payment_id,
    created_at
)
SELECT
    gen_random_uuid(),
    r.id,
    r.user_id,
    r.payment_method_id,
    COALESCE(r.final_amount, 100),
    'RUB',

    CASE
        WHEN r.payment_status = 'PAID' THEN 'PAID'
        WHEN r.payment_status = 'FAILED' THEN 'FAILED'
        ELSE 'PENDING'
    END,

    CASE
        WHEN random() < 0.5 THEN 'YooKassa'
        ELSE 'Sberbank'
    END,

    'pay_' || substr(md5(random()::text),1,16),

    r.created_at + interval '1 hour'
FROM rentals r
WHERE NOT EXISTS (
    SELECT 1
    FROM payments p
    WHERE p.rental_id = r.id
);


INSERT INTO cell_events (
    id,
    cell_id,
    rental_id,
    event_type,
    payload_json,
    created_at
)
SELECT
    gen_random_uuid(),
    r.cell_id,
    r.id,

    (ARRAY[
        'cell_opened',
        'cell_closed',
        'status_changed'
    ])[floor(random()*3+1)],

    jsonb_build_object(
        'source', 'mobile_app',
        'generated', true
    ),

    NOW() - (random() * interval '30 days')
FROM rentals r
CROSS JOIN generate_series(1,3);


INSERT INTO hardware_events (
    id,
    cell_id,
    event_type,
    raw_payload,
    processed,
    created_at
)
SELECT
    gen_random_uuid(),

    (SELECT id
     FROM locker_cells
     ORDER BY random()
     LIMIT 1),

    (ARRAY[
        'door_opened',
        'door_closed',
        'heartbeat',
        'sensor_update',
        'sensor_error'
    ])[floor(random()*5+1)],

    jsonb_build_object(
        'temperature', round((20 + random()*10)::numeric, 1),
        'battery', floor(50 + random()*50)
    ),

    random() > 0.1,

    NOW() - (random() * interval '30 days')
FROM generate_series(1,500);

SELECT count(*) FROM users;
SELECT count(*) FROM locker_stations;
SELECT count(*) FROM locker_cells;
SELECT count(*) FROM payment_methods;
SELECT count(*) FROM rentals;
SELECT count(*) FROM payments;
SELECT count(*) FROM cell_events;
SELECT count(*) FROM hardware_events;
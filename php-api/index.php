<?php
header('Content-Type: application/json');

$orderApiUrl = 'http://orders:3002/order';

try {
    // Faz a chamada à API de Pedidos
    $orderResponse = file_get_contents($orderApiUrl);
    
    if ($orderResponse === FALSE) {
        throw new Exception("Falha ao acessar API de Pedidos");
    }

    $orderData = json_decode($orderResponse, true);
    
    // Simula processamento de pagamento
    $response = [
        'status' => 'paid',
        'order' => $orderData,
        'payment_id' => uniqid(),
        'timestamp' => date('c')
    ];

    echo json_encode($response, JSON_PRETTY_PRINT);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>
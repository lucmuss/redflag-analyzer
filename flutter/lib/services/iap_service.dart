import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:logger/logger.dart';
import 'dart:async';

import '../config/app_config.dart';

/// In-App Purchase Service
/// Handles credit purchases via Apple App Store and Google Play
class IAPService {
  final InAppPurchase _iap = InAppPurchase.instance;
  final Logger _logger = Logger();
  
  StreamSubscription<List<PurchaseDetails>>? _subscription;
  bool _isAvailable = false;
  List<ProductDetails> _products = [];
  
  // Product IDs
  static const String creditProductId = AppConfig.iapProductIdAndroid;
  
  /// Initialize IAP
  Future<void> init() async {
    try {
      _isAvailable = await _iap.isAvailable();
      
      if (!_isAvailable) {
        _logger.w('IAP not available on this device');
        return;
      }
      
      // Listen to purchase updates
      _subscription = _iap.purchaseStream.listen(
        _handlePurchaseUpdates,
        onError: (error) {
          _logger.e('IAP stream error: $error');
        },
      );
      
      // Load products
      await _loadProducts();
      
      _logger.d('IAP initialized successfully');
    } catch (e) {
      _logger.e('Failed to initialize IAP: $e');
    }
  }
  
  /// Load available products
  Future<void> _loadProducts() async {
    try {
      const Set<String> productIds = {creditProductId};
      
      final ProductDetailsResponse response = 
          await _iap.queryProductDetails(productIds);
      
      if (response.error != null) {
        _logger.e('Error loading products: ${response.error}');
        return;
      }
      
      _products = response.productDetails;
      
      if (_products.isEmpty) {
        _logger.w('No products found');
      } else {
        _logger.d('Loaded ${_products.length} products');
      }
    } catch (e) {
      _logger.e('Failed to load products: $e');
    }
  }
  
  /// Purchase credit
  Future<bool> purchaseCredit() async {
    if (!_isAvailable) {
      _logger.w('IAP not available');
      return false;
    }
    
    if (_products.isEmpty) {
      _logger.w('No products available');
      return false;
    }
    
    try {
      final ProductDetails product = _products.first;
      
      final PurchaseParam purchaseParam = PurchaseParam(
        productDetails: product,
      );
      
      final bool success = await _iap.buyConsumable(
        purchaseParam: purchaseParam,
      );
      
      _logger.d('Purchase initiated: $success');
      return success;
    } catch (e) {
      _logger.e('Purchase failed: $e');
      return false;
    }
  }
  
  /// Handle purchase updates
  void _handlePurchaseUpdates(List<PurchaseDetails> purchases) {
    for (final PurchaseDetails purchase in purchases) {
      _logger.d('Purchase update: ${purchase.status}');
      
      if (purchase.status == PurchaseStatus.purchased) {
        // Verify purchase with backend
        _verifyPurchase(purchase);
      } else if (purchase.status == PurchaseStatus.error) {
        _logger.e('Purchase error: ${purchase.error}');
      }
      
      // Complete pending purchases
      if (purchase.pendingCompletePurchase) {
        _iap.completePurchase(purchase);
      }
    }
  }
  
  /// Verify purchase with backend
  Future<void> _verifyPurchase(PurchaseDetails purchase) async {
    try {
      // TODO: Send purchase receipt to backend for verification
      // await apiService.verifyPurchase(purchase.verificationData);
      
      _logger.d('Purchase verified: ${purchase.productID}');
      
      // Credit will be added by backend after verification
    } catch (e) {
      _logger.e('Purchase verification failed: $e');
    }
  }
  
  /// Restore purchases
  Future<void> restorePurchases() async {
    if (!_isAvailable) return;
    
    try {
      await _iap.restorePurchases();
      _logger.d('Purchases restored');
    } catch (e) {
      _logger.e('Failed to restore purchases: $e');
    }
  }
  
  /// Get product price
  String? getProductPrice() {
    if (_products.isEmpty) return null;
    return _products.first.price;
  }
  
  /// Dispose
  void dispose() {
    _subscription?.cancel();
  }
  
  // Getters
  bool get isAvailable => _isAvailable;
  List<ProductDetails> get products => _products;
}

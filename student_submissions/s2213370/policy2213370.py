from policy import Policy
import numpy as np

class Policy2213370(Policy):
    def __init__(self, policy_id=1):
        """
        Hàm khởi tạo của Policy, đảm bảo policy_id chỉ nhận giá trị 1 hoặc 2.
        """
        assert policy_id in [1, 2]
        self.policy_id = policy_id

    def _get_stock_size_(self, stock):
        """
        Tính toán chiều rộng và chiều cao khả dụng của kho.
        """
        stock_w = np.sum(np.any(stock != -2, axis=1))  
        stock_h = np.sum(np.any(stock != -2, axis=0))  
        return stock_w, stock_h

    def _can_place_(self, stock, position, prod_size):
        """
        Kiểm tra xem sản phẩm có thể được đặt tại vị trí chỉ định hay không.
        """
        pos_x, pos_y = position
        prod_w, prod_h = prod_size
        
        return np.all(stock[pos_x : pos_x + prod_w, pos_y : pos_y + prod_h] == -1)

    def _find_bottom_left_position(self, stock, prod_size, stock_w, stock_h):
        """
        Tìm vị trí thấp nhất và gần bên trái nhất để đặt sản phẩm.
        """
        prod_w, prod_h = prod_size
        best_position = None
        best_y = stock_h  

        for pos_x in range(stock_w - prod_w + 1):  
            for pos_y in range(stock_h - prod_h + 1):  
                
                if self._can_place_(stock, (pos_x, pos_y), prod_size):
                    if pos_y < best_y or (pos_y == best_y and pos_x < best_position[0]):
                        best_position = (pos_x, pos_y)
                        best_y = pos_y
        return best_position  


    def get_action(self, observation, info):
        """
        Thực hiện thuật toán Bottom-Left để đặt sản phẩm lên các kho.
        """
        list_prods = observation["products"]  
        stocks = observation["stocks"]       

        list_prods = sorted(list_prods, key=lambda prod: prod["size"][0] * prod["size"][1], reverse=True)

        for prod_idx, prod in enumerate(list_prods):
            if prod["quantity"] > 0:  
                prod_size = prod["size"]  
                for stock_idx, stock in enumerate(stocks):
                    
                    stock_w, stock_h = self._get_stock_size_(stock)
                    prod_w, prod_h = prod_size

                    position = self._find_bottom_left_position(stock, prod_size, stock_w, stock_h)
                    if position is not None:
                        return {"stock_idx": stock_idx, "size": prod_size, "position": position}

                    position = self._find_bottom_left_position(stock, prod_size[::-1], stock_w, stock_h)
                    if position is not None:
                        return {"stock_idx": stock_idx, "size": prod_size[::-1], "position": position}

        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}



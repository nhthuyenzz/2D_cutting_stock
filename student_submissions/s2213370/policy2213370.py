from policy import Policy
import numpy as np

class Policy2213370(Policy):
    def __init__(self, policy_id=1):
        """
        Hàm khởi tạo của Policy, đảm bảo policy_id chỉ nhận giá trị 1 hoặc 2.
        """
        assert policy_id in [1, 2], "Policy ID phải là 1 hoặc 2"
        self.policy_id = policy_id

    def get_action(self, observation, info):
        """
        Thực hiện thuật toán Bottom-Left để đặt sản phẩm lên các kho.
        """
        list_prods = observation["products"]  # Danh sách các sản phẩm cần đặt
        stocks = observation["stocks"]       # Danh sách các kho

        # Sắp xếp sản phẩm theo diện tích từ lớn đến nhỏ để ưu tiên đặt trước
        sorted_products = sorted(
            [(prod_idx, prod) for prod_idx, prod in enumerate(list_prods) if prod["quantity"] > 0],
            key=lambda p: p[1]["size"][0] * p[1]["size"][1],
            reverse=True,
        )

        for prod_idx, prod in sorted_products:
            prod_size = prod["size"]  # Kích thước sản phẩm
            for stock_idx, stock in enumerate(stocks):
                # Lấy kích thước thực tế của kho
                stock_w, stock_h = self._get_stock_size_(stock)
                prod_w, prod_h = prod_size

                # Thử đặt sản phẩm mà không xoay
                position = self._find_bottom_left_position(stock, prod_size, stock_w, stock_h)
                if position is not None:
                    return {"stock_idx": stock_idx, "size": prod_size, "position": position}

                # Thử đặt sản phẩm sau khi xoay
                position = self._find_bottom_left_position(stock, prod_size[::-1], stock_w, stock_h)
                if position is not None:
                    return {"stock_idx": stock_idx, "size": prod_size[::-1], "position": position}

        # Nếu không thể đặt, trả về hành động mặc định (không thực hiện gì)
        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}

    def _find_bottom_left_position(self, stock, prod_size, stock_w, stock_h):
        """
        Tìm vị trí thấp nhất và gần bên trái nhất để đặt sản phẩm.
        """
        prod_w, prod_h = prod_size
        for pos_x in range(stock_w - prod_w + 1):  # Duyệt các vị trí theo chiều rộng
            for pos_y in range(stock_h - prod_h + 1):  # Duyệt các vị trí theo chiều cao
                if self._can_place_(stock, (pos_x, pos_y), prod_size):  # Kiểm tra nếu có thể đặt
                    return pos_x, pos_y
        return None  # Không tìm được vị trí phù hợp

    def _get_stock_size_(self, stock):
        """
        Tính toán chiều rộng và chiều cao khả dụng của kho.
        """
        stock_w = np.sum(np.any(stock != -2, axis=1))  # Chiều rộng
        stock_h = np.sum(np.any(stock != -2, axis=0))  # Chiều cao
        return stock_w, stock_h

    def _can_place_(self, stock, position, prod_size):
        """
        Kiểm tra xem sản phẩm có thể được đặt tại vị trí chỉ định hay không.
        """
        pos_x, pos_y = position
        prod_w, prod_h = prod_size
        # Kiểm tra toàn bộ vùng đặt có trống (giá trị == -1)
        return np.all(stock[pos_x : pos_x + prod_w, pos_y : pos_y + prod_h] == -1)

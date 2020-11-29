from stock_class import Stock
import random


# These function is used to add a stock onto the portfolio, it accepts a ticker and a weighting, 
    #                   currently only around 10 stocks can be added due to floating point error of the weightings (This will be updated)
def add_stock(self, stock_ticker, weight, mode='equal'):
        
        buffer_list = [stock_ticker, float('{0:.12f}'.format(weight)), Stock(stock_ticker, self.start_date, self.end_date)]
        self.add_weight(buffer_list[1], mode)

        self.portfolio = np.vstack([self.portfolio, buffer_list])
        if not self.check_weighting():
            print("Error: Weights Do Not Add to 100%") 

            
    # This method is used to readjust the weights for when a stock is added, it is a work in progress and cannot currently handle more than a few stocks
    #                                                                                                                       due to floating point error
def add_weight(self, weight, mode="equal"):
        
        factor = 10000000.0
        
        if mode == 'equal':
            
            # Creates a New List adding the new value and scaling down proportionally the old values and then scaling
            #                   all numbers up by a factor of ten for floating point issues
            new_list = [round(float(val) * float(factor - (factor * weight))) for val in self.portfolio[:,1]]
            new_list.append(round(float(weight) * factor))
            counter = len(new_list) - 1
            
            # Calculates the error difference of the expected and actual totals
            difference = sum(new_list) - factor


            # This section is designed to adjust for rounding errors by making sure everything adds up to 100% evenly. It definitely needs some attention
            #       The if block checks to see if the difference can be evenly spread to all the other members of the list, it also checks if the difference
            #                 is zero. The else block handles an uneven division using floor division and randomly assigned remainder
            #
            if difference != 0:
                if difference % (counter) == 0:
                    for num in range(0, len(new_list) - 1):
                        new_list[num] -= difference / (counter)
                else:

                    floor_div = difference // counter
                    diff_of_difference = difference - (counter * floor_div)

                    for num in range(0, len(new_list) - 1):
                        new_list[num] -= floor_div
                        new_list[num] = float('{0:.12f}'.format(float(new_list[num])))

                    rand_int = random.randint(0, counter - 1)
                    new_list[rand_int] -= float('{0:.12f}'.format(float(diff_of_difference)))
                    new_list[rand_int] = float('{0:.12f}'.format(new_list[rand_int]))

            # Divides out the factor of 10 from the weights so the output is a decimal
            counter = 0
            for weights in self.portfolio[:,1]: 
                self.portfolio[counter, 1] = float('{0:.12f}'.format(float(new_list[counter]) / factor))
                counter += 1
    
    
    # This function is used to subtract a stock from a portfolio, it accepts either a ticker or a stock object
    #
def subtract_stock(self, stock, mode="equal"):
        if stock == str(stock):
            ticker = stock
        else:
            ticker = stock.ticker
        # remove stock coming soon
    

    # A function to subtract a weight and readjust the other weights proportionally
def subtract_weight(self, mode, weight):
        print("Coming Soon")
        
     # Just updates the count, for internal methods
def update_num_stocks(self):
        self.stock_count = len(self)
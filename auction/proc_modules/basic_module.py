from foundation.module import Module
from foundation.field_value import FieldValue
from foundation.parse_format import ParseFormats
from foundation.config_param import ConfigParam
from foundation.bidding_object import BiddingObject
from foundation.auction import AuctioningObjectType

from datetime import datetime
from utils.auction_utils import log
from typing import Dict
from typing import List


class BasicModule(Module):


    def __init__(self, module_name:str, module_file:str, module_handle, config_group:str):
        super(BasicModule,self).__init__(module_name, module_file, module_handle, config_group)
        self.config_param_list = {}
        self.logger = log().get_logger()
        self.bandwidth = 0
        self.reserved_price = 0
        self.domain = 0

    def init_module(self, config_param_list:Dict[str, ConfigParam]):
        self.logger.debug('in init_module')
        self.config_param_list = config_param_list
        self.domain = config_param_list['domainid']

    def get_resource_avalability(self):
        self.logger.debug('Starting getResourceAvailability')

        self.bandwidth = ParseFormats.parse_float(self.config_param_list['bandwidth'].value)

        if self.bandwidth <= 0:
            raise ValueError("bas init module - The given bandwidth parameter is incorrect");

        return self.bandwidth

    def get_reserved_price(self):
        self.logger.debug('Starting get_reserved_price')

        self.reserved_price = ParseFormats.parse_double(self.config_param_list['reserveprice'].value)

        if (self.reserved_price < 0):
            raise ValueError("bas init module - The given reserve price is incorrect")

        return self.reserved_price

    def make_key(self, auction_key: str, bid_key: str) -> str:
        return auction_key + '-' + bid_key

    def create_allocation(self, session_id: str, auction_key: str, start: datetime,
                                stop: datetime, quantity: float, price: float):

        self.logger("bas module: start create allocation")

        elements = dict()
        config_elements = dict()

        # Insert quantity ipap_field
        record_id = "record_1";
        self.proc_module.insert_string_field("recordid", record_id, config_elements)
        self.proc_module.insert_float_field("quantity", quantity, config_elements)
        self.proc_module.insert_double_field("unitprice", price, config_elements)
        elements[record_id] = config_elements

        # construct the interval with the allocation, based on start datetime
        # and interval for the requesting auction

        options = dict()
        option_id = 'option_1'
        config_options = dict()

        self.proc_module.insert_string_field("recordid", option_id, config_elements)
        self.proc_module.insert_datetime_field("start", start, config_options)
        self.proc_module.insert_datetime_field("stop", stop, config_options)
        options[option_id] = config_options

        bidding_object_id = self.proc_module.get_bidding_object_id()
        bidding_object_key = str(self.domain) + '.' + bidding_object_id
        alloc = BiddingObject(auction_key, bidding_object_key, AuctioningObjectType.ALLOCATION, elements, options)

        # All objects must be inherit the session from the bid.
        alloc.set_session(session_id)

        return alloc;

    def increment_quantity_allocation(self, allocation: BiddingObject, quantity: float):

        self.logger.debug("bas module: starting increment quantity allocation")
        elements = allocation.elements

        # there is only one element
        field = None
        for element_name in elements:
            config_dict = elements[element_name]
            field: ConfigParam = config_dict.pop('quantity')
            break

        # Insert the field again.
        if field:
            # Insert again the field.
            temp_qty = ParseFormats.parse_float(field.value)
            temp_qty += quantity
            fvalue = str(temp_qty)
            field.value = fvalue
            config_dict[field.name] = field
        else:
            raise ValueError("Field quantity was not included in the allocation")

        self.logger.debug("bas module: ending increment quantity allocation")

    def calculate_requested_quantities(self, bidding_objects: List[BiddingObject]):

        self.logger.debug("bas module: starting calculateRequestedQuantities")
        sum_quantity = 0
        for bidding_object in bidding_objects:
            elements = bidding_object.elements
            for element_name in elements:
                config_dict = elements[element_name]
                quantity = float(config_dict['quantity'].value)
                sum_quantity = sum_quantity + quantity

        self.logger.debug("bas module - ending calculateRequestedQuantities: {0}".format(sum_quantity))
        return sum_quantity

    def get_bid_price(self, bidding_object: BiddingObject):
        unit_price = -1

        elements = bidding_object.elements
        for element_name in elements:
            config_dict = elements[element_name]
            unit_price = float(config_dict['unitprice'].value)
            break
        return unit_price

    def separate_bids(self, bidding_objects: List[BiddingObject], bh: float, bl: float ) -> (List[BiddingObject],
                                                                                             List[BiddingObject]):
        self.logger.debug("bas module: Starting separateBids")
        bids_high = []
        bids_low = []
        for bidding_object in bidding_objects:

            price = self.get_bid_price(bidding_object)

            if price >= 0:
                if price > bl:
                    bids_high.append(bidding_object)
                else:
                    bids_low.append(bidding_object)

        self.logger.debug("bas module: Ending separateBids")
        return bids_low, bids_high

    def destroy_module(self):
        print ('in destroy_module')

    def execute(self, auction_key: str, start:datetime, stop:datetime, bids: dict) -> dict:
        self.logger.debug("bas module: start execute num bids:{0}".format(str(len(bids))))

        tot_demand = self.calculate_requested_quantities(bids)
        bandwidth_to_sell = self.get_resource_availability(params)
        reserve_price = self.get_reserve_price(params)

        bids_low_rct = []
        bids_high_rct = []

        # Order bids classifying them by whether they compete on the low and high auction.
        bids_low_rct, bids_high_rct = self.separate_bids(bids, 0.5, 1)

        # Calculate the number of bids on both auctions.
        nl = self.calculate_requested_quantities(bids_low_rct)
        nh = self.calculate_requested_quantities(bids_high_rct)

        std::multimap < double, alloc_proc_t > orderedBids;
        # Order bids by elements.
        auction::auctioningObjectDBIter_t bid_iter;

        for bidding_object_key in bids:
            bidding_object = bids[bidding_object_key]
            elements = bidding_object.elements
            for elemen_name in elements:
                config_params = elements[elemen_name]
                price = config_params["unitprice"]
                quantity = config_params["quantity"]

                alloc_proc_t alloc;

                alloc.bidSet = bid->getSet();
                alloc.bidName = bid->getName();
                alloc.elementName = elem_iter->first;
                alloc.sessionId = bid->getSession();
                alloc.quantity = quantity;
                orderedBids.insert(make_pair(price, alloc));


        qty_available = bandwidth_to_sell
        sellPrice = 0

        self.logger.debug("bas module - qty available:{0}".format(qty_available))

        std::multimap < double, alloc_proc_t >::iterator
        it = orderedBids.end();
        do
        {
            --it;

            if it->first < reserve_price:
                (it->second).quantity = 0
            else:

                if qty_available < (it->second).quantity:
                    (it->second).quantity = qty_available
                    if qty_available > 0:
                        sellPrice = it->first
                        qtyAvailable = 0
                else:
                    qtyAvailable = qtyAvailable - (it->second).quantity
                    sellPrice = it->first

        } while (it != orderedBids.begin())

        # There are more units available than requested
        if (qtyAvailable > 0):
            sellPrice = reserve_price

        self.logger.debug("bas module: after executing the auction")

        map < string, auction::BiddingObject * > allocations;
        map < string, auction::BiddingObject * >::iterator alloc_iter;

        # Creates allocations
        it = orderedBids.end();
        do
        {
            --it;

            if (allocations.find(makeKey(aset,
                                         aname, (it->second).bidSet, (it->second).bidName)) != allocations.end()):
                alloc_iter = allocations.find(makeKey(aset, aname,
                (it->second).bidSet, (it->second).bidName ))
                incrementQuantityAllocation(fieldVals, alloc_iter->second, (it->second).quantity)
            else:
                auction::
                    BiddingObject * alloc =
                    createAllocation(fieldDefs, fieldVals, aset, aname,
                                     (it->second).bidSet, (it->second).bidName, (it->second).sessionId,
                                     start, stop, (it->second).quantity, sellPrice)

                allocations[makeKey(aset, aname,
                                    (it->second).bidSet, (it->second).bidName)] = alloc

        } while (it != orderedBids.begin())

        # Convert from the map to the final allocationDB result
        for (alloc_iter = allocations.begin(); alloc_iter != allocations.end(); ++alloc_iter ):
            (*allocationdata)->push_back(alloc_iter->second)

        # Write a log with data of the auction

        std::ofstream fs;
        string filename = aset + "_" + aname + "_" + "_bas.txt";
        fs.open(filename.c_str(), ios::app);
        if (!fs.fail()){
            fs << "starttime:" << start << ":endtime:" << stop;
            fs << ":demand:" << totDemand << ":demand_low:" << nl << ":demand_high:" << nh;
            fs << ":qty_sell:" << bandwidth_to_sell - qtyAvailable;
            fs << ":reservedPrice:" << reserve_price << ":sell price:" << sellPrice << "\n";
            fs.close( );
        }

        delete bids_low_rct;
        delete bids_high_rct;

        self.logger.debug("bas module: end execute")

    def execute_user(self, request_params: Dict[str, FieldValue], auctions: dict,
                     start: datetime, stop: datetime) -> list:
        print('in execute_user')
        pass

    def reset(self):
        print('in reset')
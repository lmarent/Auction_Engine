
# Variables given as parameters.
uint32_t lastId;
ipap_field_container g_ipap_fields;
/*! auction = 0 if the auction corresponds to low budget
 * 			= 1 if the auction corresponds to high budget
*/

class TwoAuctionGeneralized(Module):

    def __init__(self, module_name: str, module_file: str, module_handle, config_group: str):
        super(TwoAuctionGeneralized, self).__init__(module_name, module_file, module_handle, config_group)
        self.config_params = {}
        self.logger = log().get_logger()
        self.bandwidth = 0
        self.reserved_price = 0
        self.domain = 0
        self.proc_module = ProcModule()

    def init_module(self, config_params: Dict[str, ConfigParam]):
        """
        Initializes the module

        :param config_params: dictionary with the given configuration parameters
        """
        self.logger.debug('in init_module')
        self.config_params = config_params
        self.domain = config_params['domainid']

    @staticmethod
    def make_key(auction_key: str, bid_key: str) -> str:
        """
        Make the key of an allocation from the auction key and bidding object key

        :param auction_key: auction key
        :param bid_key: bidding object key
        :return:
        """
        return auction_key + '-' + bid_key






time_t getTime(auction::configParam_t *p arams, string name )
{
    time_t tim = 0;
    int numparams = 0;

    # ifdef DEBUG
    cout << "get time - field:" << name << endl;
    # endif

    while (params[0].name != NULL) {
        if (!strcmp(params[0].name, name.c_str())) {
            tim = (time_t) parseTime(params[0].value);
            numparams++;
        }
        params++;
    }

    if (numparams == 0)
        throw
        auction::ProcError(AUM_PROC_PARAMETER_ERROR,
                           "two auction generalized init module - not enought parameters");

    if (tim == 0)
        throw
        auction::ProcError(AUM_DATETIME_NOT_DEFINED_ERROR,
                           "two auction generalized init module - The given time is incorrect");

        # ifdef DEBUG
    cout << "get time" << tim << endl;
    # endif

    return tim;

}

    def destroy_module(self):
        """
        method to be executed when destroying the class
        :return:
        """
        self.logger.debug('in destroy_module')


    def create_allocation(self, session_id: str, auction_key: str, start: datetime,
                          stop: datetime, quantity: float, price: float) -> BiddingObject:
        """
        Creates a new allocation

        :param session_id: session id to be associated
        :param auction_key: auction key
        :param start: allocation's start
        :param stop: allocation's stop
        :param quantity: quantity to assign
        :param price: price to pay
        :return: Bidding object
        """
        self.logger.debug("bas module: start create allocation")

        elements = dict()
        config_elements = dict()

        # Insert quantity ipap_field
        record_id = "record_1"
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

        return alloc


string getBidName(string allocationKey)
{
    cout << "start getBidName" << endl;

    std::size_t found = allocationKey.find_last_of("|");
    string bidName = allocationKey.substr(found+ 1 );

    cout << "ending getBidName:" << bidName << endl;
    return bidName;
}


double
getProbability()
{
    cout << "start getProbability:" << endl;

    unsigned int nbr;

    int ret = RAND_bytes((unsigned char *) & nbr, sizeof(nbr));

    assert (ret == 1);

    unsigned long umin = numeric_limits < unsigned int >::min();
    unsigned long umax = numeric_limits < unsigned int >::max();

    double dumin = umin;
    double dumax = umax;
    double prob = nbr / (dumax - dumin);

    cout << "ending getProbability:" << prob << endl;

    return prob;
}


double
getAllocationQuantity(auction::fieldValList_t * fieldVals, auction::BiddingObject * allocation)
{
    # ifdef DEBUG
    fprintf(stdout, "two auction module: starting getAllocationQuantity \n");
    # endif

    float temp_qty = 0;
    auction::elementList_t * elements = allocation->getElements();

    // there is only one element.
    auction::fieldListIter_t field_iter;
    auction::field_t field;
    for (field_iter = (elements->begin()->second).begin(); field_iter != (elements->begin()->second).end(); ++field_iter ){
        if ((field_iter->name).compare("quantity") == 0)
        {
            field = *field_iter;
            temp_qty = parseFloat(((field.value)[0]).getValue());
            break;
        }
    }

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: ending getAllocationQuantity \n");
    # endif

    return temp_qty;

}

double getBidPrice(auction::BiddingObject * bid)
{

    double unitPrice = -1;
    auction::elementList_t * elems = bid->getElements();

    auction::elementListIter_t elem_iter;
    for (elem_iter = elems->begin(); elem_iter != elems->end(); ++elem_iter )
    {
        unitPrice = getDoubleField( & (elem_iter->second), "unitprice");
        break;
    }

    return unitPrice;

}


int calculateRequestedQuantities(auction::auctioningObjectDB_t * bids)
{

    # ifdef DEBUG
    cout << "two auction generalized module: starting calculateRequestedQuantities" << endl;
    # endif

    int sumQuantity = 0;

    auction::auctioningObjectDBIter_t bid_iter;
    for (bid_iter = bids->begin(); bid_iter != bids->end(); ++bid_iter){
        auction:: BiddingObject * bid = dynamic_cast < auction::BiddingObject * > (*bid_iter);
        auction::elementList_t * elems = bid->getElements();
        auction::elementListIter_t
        elem_iter;

        for (elem_iter = elems->begin(); elem_iter != elems->end(); ++elem_iter )
        {
            int quantity = floor(getDoubleField( & (elem_iter->second), "quantity"));
            sumQuantity = sumQuantity + quantity;
        }
    }

    # ifdef DEBUG
    cout << "two auction generalized module: ending calculateRequestedQuantities" << sumQuantity << endl;
    # endif

    return sumQuantity;
}

void createRequest(auction::auctioningObjectDB_t * bids_low, auction::auctioningObjectDB_t * bids_high,
                   LAuctionRequestDB_t & lrequest, HAuctionRequestDB_t & hrequest, double qStar, double
                   reserve_price_low, int * nh, int * nl)
{

    # ifdef DEBUG
    cout << "create requests" << endl;
    # endif

    int nhtmp = 0;
    int nltmp = 0;

    # creates the request for the L auction.
    int index = 0;
    auction::auctioningObjectDBIter_t bid_iter;
    for (bid_iter = bids_low->begin(); bid_iter != bids_low->end(); ++bid_iter)
    {
        auction:: BiddingObject * bid = dynamic_cast < auction::BiddingObject * > (*bid_iter);
        auction::elementList_t * elems = bid->getElements();
        auction::elementListIter_t elem_iter;
        int j = 0;
        for (elem_iter = elems->begin(); elem_iter != elems->end(); ++elem_iter )
        {

            double price = getDoubleField( & (elem_iter->second), "unitprice");
            double quantity = getDoubleField( & (elem_iter->second), "quantity");

            if (quantity > 0) {
            alloc_proc_t alloc;
            alloc.bidSet = bid->getSet();
            alloc.bidName = bid->getName();
            alloc.elementName = elem_iter->first;
            alloc.sessionId = bid->getSession();
            alloc.quantity = quantity;
            alloc.originalPrice = price;
            lrequest[index][j] = alloc;
            j = j + 1;
            nltmp = nltmp + quantity;
            }
        }

        # Only increase index if there was another node inserted.
        if (j >= 1){
            index = index + 1;
        }
    }

    # ifdef DEBUG
    cout << "create requests after low budget bids" << endl;
    # endif


    # go through all high budget bids and pass some of their units as low auction requests.

    for (bid_iter = bids_high->begin(); bid_iter != bids_high->end(); ++bid_iter){
        auction::BiddingObject * bid = dynamic_cast < auction::BiddingObject * > (*bid_iter);
        auction::elementList_t * elems = bid->getElements();
        int j = 0;
        allocforbidDB_t allocBid;
        auction::elementListIter_t elem_iter;
        for (elem_iter = elems->begin(); elem_iter != elems->end(); ++elem_iter )
        {
            double price = getDoubleField( & (elem_iter->second), "unitprice");
            double quantity = getDoubleField( & (elem_iter->second), "quantity");

            float unitsToPass = 0;
            for (int k = 0; k < quantity; k++)
            {

                if (getProbability() <= qStar) # pass a unit.
                    unitsToPass = unitsToPass + 1;

            }

            # quantities in the H auction.
            alloc_proc_t alloc1;
            alloc1.bidSet = bid->getSet();
            alloc1.bidName = bid->getName();
            alloc1.elementName = elem_iter->first;
            alloc1.sessionId = bid->getSession();
            alloc1.quantity = quantity - unitsToPass;
            alloc1.originalPrice = price;
            hrequest.insert(make_pair(price, alloc1));
            nhtmp = nhtmp + quantity - unitsToPass;

            # quantities in the L auction.
            alloc_proc_t alloc2;
            alloc2.bidSet = bid->getSet();
            alloc2.bidName = bid->getName();
            alloc2.elementName = elem_iter->first;
            alloc2.sessionId = bid->getSession();
            alloc2.quantity = unitsToPass;
            alloc2.originalPrice = price;
            allocBid.push_back(alloc2);
            j = j + 1;

            cout << "bid set:" << bid->getSet() << "units pass:" << unitsToPass << endl;
            nltmp = nltmp + unitsToPass;
        }

        # Only increase index if there was another node inserted.
        if (j >= 1)
        {

            lrequest.push_back(allocBid);
            index = index + 1;
        }

    }

    *nl = nltmp;
    *nh = nhtmp;

    # ifdef DEBUG
    cout << "ending create requests -nl:" << *nl << "nh:" << *nh << endl;
    # endif

}

    def executeAuctionRandomAllocation(self, price: float, auction_key: str, start: datetime, stop:datetime,
                                       LAuctionRequestDB_t & bidsToFulfil, qty_available: float,
                                       map < string, auction::BiddingObject * > & allocations):

        self.logger.debug("execute Action random allocation")

        double prob;
        map < string, auction::BiddingObject * >::iterator alloc_iter;

        int index;

        # Create allocations for Bids that are below the reserved price.
        for (int m = bidsToFulfil.size() - 1; m >= 0; m--){
            self.logger.debug("execute Action random allocation 1")
            for (int l = (bidsToFulfil[m]).size()-1; l >= 0; l--){
                self.logger.debug("execute Action random allocation m: {0} l:{1}".format(str(m), str(l)))
                if ((bidsToFulfil[m][l]).originalPrice < price){
                    if ( allocations.find(makeKey(aset, aname, (bidsToFulfil[m][l]).bidSet, (bidsToFulfil[m][l]).bidName )) == allocations.end()) {
                        auction::BiddingObject * alloc = \
                        createAllocation(fieldDefs, fieldVals, aset, aname, (bidsToFulfil[m][l]).bidSet,
                                 (bidsToFulfil[m][l]).bidName, (bidsToFulfil[m][l]).sessionId,
                                 start, stop, 0, price);

                    allocations[makeKey(aset, aname,
                            (bidsToFulfil[m][l]).bidSet, (bidsToFulfil[m][l]).bidName)] = alloc;
                    }
                    original_price = bidsToFulfil[m][l]).originalPrice
                    self.logger.debug("execute Action random allocation 2 - item:{0} original price:{1}".format(str(l), str(original_price)))


                    # Remove the node.
                    bidsToFulfil[m].erase((bidsToFulfil[m]).begin() + l);
                }
            }

            self.logger.debug("execute Action random allocation 2")
            # Remove the bid if all their price elements were less than the reserved price.
            if (bidsToFulfil[m]).size() == 0:
                bidsToFulfil.erase(bidsToFulfil.begin() + m);

            self.logger.debug("execute Action random allocation 3")
        }

        # Allocates randomly the available quantities
        for (int j = 0; j < qtyAvailable; j++){

            prob = getProbability();
            index = floor(prob * bidsToFulfil.size());
            if (bidsToFulfil.size() == 0){
                # All units have been assigned and there are no more bids.
                break;
            }
            else {
                # The unit is assigned to the first allocation proc for the bid.
                (bidsToFulfil[index][0]).quantity - -;

                # Create or update the allocation
                if (allocations.find(makeKey(aset, aname, (bidsToFulfil[index][0]).bidSet, (bidsToFulfil[index][0]).bidName)) != allocations.end()){
                    alloc_iter = allocations.find(makeKey(aset, aname, (bidsToFulfil[index][0]).bidSet, (bidsToFulfil[index][0]).bidName ));
                    addQuantityAllocation(fieldVals, alloc_iter->second, 1);
                }
                else {
                    auction::BiddingObject * alloc = \
                        createAllocation(fieldDefs, fieldVals, aset, aname, (bidsToFulfil[index][0]).bidSet,
                                 (bidsToFulfil[index][0]).bidName, (bidsToFulfil[index][0]).sessionId,
                                 start, stop, 1, price);

                    allocations[makeKey(aset, aname,
                            (bidsToFulfil[index][0]).bidSet, (bidsToFulfil[index][0]).bidName)] = alloc;
                }

                # Remove the node in case of no more units required.
                if ((bidsToFulfil[index][0]).quantity == 0){
                    (bidsToFulfil[index]).erase(bidsToFulfil[index].begin());
                    if ((bidsToFulfil[index]).size() == 0){
                        bidsToFulfil.erase(bidsToFulfil.begin() + index);
                    }
                }
            }
        }

        self.logger.debug("execute Action random allocation")


double executeAuction(auction::fieldDefList_t * fieldDefs, auction::fieldValList_t * fieldVals, string aset,
                      string aname, time_t start, time_t stop, HAuctionRequestDB_t & orderedBids, double qtyAvailable,
                      map < string, auction::BiddingObject * > & allocations, double reservedPrice)
{

    double sellPrice = 0;

    # ifdef DEBUG
    cout << "two auction generalized module- qty available:" << qtyAvailable << endl;
    # endif

    if (orderedBids.size() > 0)
    {
        std:: multimap < double, alloc_proc_t >::iterator it = orderedBids.end();
        do
        {
            --it;

            if (it->first < reservedPrice){
                (it->second).quantity = 0;
                sellPrice = reservedPrice;
            }
            else {
                if ( qtyAvailable < (it->second).quantity){
                    (it->second).quantity = qtyAvailable;
                    if (qtyAvailable > 0){
                        sellPrice = it->first;
                        qtyAvailable = 0;
                    }
                }
                else {
                    qtyAvailable = qtyAvailable - (it->second).quantity;
                    sellPrice = it->first;
                }
            }
        } while (it != orderedBids.begin());

        map < string, auction::BiddingObject * >::iterator alloc_iter;

        # Creates allocations
        it = orderedBids.end();
        do
        {
            --it;

            if (allocations.find(makeKey(aset,
                                         aname, (it->second).bidSet, (it->second).bidName)) != allocations.end())
            {
                alloc_iter = allocations.find(makeKey(aset, aname,
                                                      (it->second).bidSet, (it->second).bidName));
                addQuantityAllocation(fieldVals, alloc_iter->second, (it->second).quantity);
            }
            else {
                auction:: BiddingObject * alloc =
                createAllocation(fieldDefs, fieldVals, aset, aname,
                             (it->second).bidSet, (it->second).bidName, (it->second).sessionId,
                             start, stop, (it->second).quantity, sellPrice);

                allocations[makeKey(aset, aname,
                                (it->second).bidSet, (it->second).bidName)] = alloc;
            }

        } while (it != orderedBids.begin());
    }
    # ifdef DEBUG
    cout << "two auction module: after create allocations" << (int)
    allocations.size() << endl;
    # endif

    return sellPrice;
}


    def apply_mechanism(self, start: datetime, stop: datetime, allocations: Dict[str, BiddingObject], price: float, Q:float):
        """
        Apply mechanism
        :param self:
        :param start:
        :param stop:
        :param allocations:
        :param price:
        :param Q:
        :return:
        """
        self.logger.debug("starting ApplyMechanism Q: {0}".format(Q))

        for bidding_object_key in allocations:
            alloc = allocations[bidding_object_key]
            quantity = floor(getAllocationQuantity(fieldVals, alloc));
            units_to_pass = 0.0
            for j in range(0, quantity):
                prob = getProbability()

                if prob <= Q: # pass a unit.
                    units_to_pass = units_to_pass + 1

            self.logger.debug("bid set: {0} qty to pass: {1}".format(alloc->getSet(), str(units_to_pass)))
            if units_to_pass > 0:
                if units_to_pass < quantity:
                    alloc2 = self.create_allocation(alloc.session_id,
                                                        alloc.auction_key,
                                                        start, stop,
                                                        units_to_pass,
                                                        price)

                    units_to_add = units_to_pass * -1
                    self.proc_module.increment_quantity_allocation(alloc, units_to_add)

                    allocations[self.makeKey(alloc2.auction_key, alloc2.bidding_object_key)] = alloc2
                else:
                    self.proc_module.change_allocation_price(alloc, price)
        self.logger.debug("ending ApplyMechanism")

    def execute(self, request_params: Dict[str, FieldValue], auction_key: str,
                start: datetime, stop: datetime, bids: dict) -> list:
        """
        Executes the auction procedure for an specific auction.

        :param request_params: request params included
        :param auction_key: auction key identifying the auction
        :param start: start datetime
        :param stop: stop datetime
        :param bids: bidding objects included
        :return:
        """

        self.logger.debug("two auction generalized module: start execute {0}".format(len(bids)))

        tot_demand = self.proc_module.calculate_requested_quantities(bids)
        bandwidth_to_sell_low = self.proc_module.get_param_value('bandwidth01', request_params)
        bandwidth_to_sell_high = self.proc_module.get_param_value('bandwidth02', request_params)

        reserve_price_low = self.proc_module.get_param_value('reserveprice01', request_params)
        reserve_price_high = self.proc_module.get_param_value('reserveprice02', request_params)

        bl = self.proc_module.get_param_value('maxvalue01', request_params)
        bh = self.proc_module.get_param_value('maxvalue02', request_params)

        tot_demand = self.proc_module.calculate_requested_quantities(bids)

        self.logger.debug("totalReq: {0} total units: {1}".format(str(tot_demand),
                                                                  str(bandwidth_to_sell_low + bandwidth_to_sell_high))))

        if tot_demand > (bandwidth_to_sell_low + bandwidth_to_sell_high):

            self.logger.debug("Splitting resources:")

            bids_low, bids_high = self.proc_module.separate_bids(bids, bl)

            # Calculate the number of bids on both auctions.
            nl = self.proc_module.calculate_requested_quantities(bids_low)
            nh = self.proc_module.calculate_requested_quantities(bids_high)

            qStar = 0
            Q = 0.2

            self.logger.debug("Starting the execution of the mechanism")

            if nl > 0 and nh > 0:

                # Find the probability of changing from the high budget to low budget auction.
                TwoAuctionMechanismGeneralized * mechanism = new TwoAuctionMechanismGeneralized();
                a = 0.01
                b = 0.8

                mechanism->zeroin(nh, nl, bh, bl, bandwidth_to_sell_high,
                    bandwidth_to_sell_low, reserve_price_high, reserve_price_low, Q, & a, & b);
                qStar = a

                while (qStar >= 0.25) and (Q <= 1.0):
                    Q = Q + 0.03
                    a = 0.01
                    b = 0.8

                    mechanism->zeroin(nh, nl, bh, bl, bandwidth_to_sell_high,
                                  bandwidth_to_sell_low, reserve_price_high, reserve_price_low, Q, & a, & b)

                    qStar = a

                    self.logger.debug("Q: {0} qStar: {1}".format(str(Q), str(qStar)))

            self.logger.debug("Finished the execution of the mechanism")

            LAuctionRequestDB_t lrequests(bids_low->size(), vector < alloc_proc_t > (1)  );
            HAuctionRequestDB_t hrequests;

            # Create requests for both auctions, it pass the users from an auction to the other.
            createRequest(bids_low, bids_high, lrequests, hrequests, qStar, reserve_price_low, & nh, & nl);

            # Execute auctions.
            map < string, auction::BiddingObject * > alloctions_low;

            executeAuctionRandomAllocation(fieldDefs, fieldVals, reserve_price_low, aset, aname, start, stop,
            lrequests, bandwidth_to_sell_low, alloctions_low);

            map < string, auction::BiddingObject * > alloctions_high;
            executeAuction(fieldDefs, fieldVals, aset, aname, start, stop, hrequests, bandwidth_to_sell_low, alloctions_high, reserve_price_high);

            cout << "after executeAuction high budget users" << endl;

            if Q > 0:
                # change bids from the high budget to low budget auction.
                self.apply_mechanism(start, stop, alloctions_high, reserve_price_low, Q)

            # Convert from the map to the final allocationDB result
            map < string, auction::BiddingObject * >::iterator alloc_iter;
            for (alloc_iter = alloctions_low.begin(); alloc_iter != alloctions_low.end(); ++alloc_iter )
            {
                (*allocationdata)->push_back(alloc_iter->second);
            }

            # Convert from the map to the final allocationDB result
            for (alloc_iter = alloctions_high.begin(); alloc_iter != alloctions_high.end(); ++alloc_iter )
            {
                (*allocationdata)->push_back(alloc_iter->second);
            }

            # Free the memory allocated to these two containers.
            delete bids_low;
            delete bids_high;
        }
        else {

            cout << "auctioning without splitting resources:" << endl;

            # All bids get units and pay the reserved price of the L Auction
            int nl, nh = 0;
            auction::auctioningObjectDB_t * bids_low = new
            auction::auctioningObjectDB_t();
            LAuctionRequestDB_t lrequests(1, vector < alloc_proc_t > (1));
            HAuctionRequestDB_t hrequests;

            createRequest(bids_low, bids, lrequests, hrequests, 0, reserve_price_low, & nh, & nl);

            map < string, auction::BiddingObject * > alloctions_high;
            executeAuction(fieldDefs, fieldVals, aset, aname, start, stop,
            hrequests, totalReq, alloctions_high, reserve_price_low);

            # Convert from the map to the final allocationDB result
            map < string, auction::BiddingObject * >::iterator alloc_iter;
            for (alloc_iter = alloctions_high.begin(); alloc_iter != alloctions_high.end(); ++alloc_iter )
            {
                (*allocationdata)->push_back(alloc_iter->second);
            }

            delete bids_low;

        }
        # ifdef DEBUG
        cout << "two auction generalized module: end execute" << endl;
        # endif

    def execute_user(self, request_params: Dict[str, FieldValue], auctions: dict,
                     start: datetime, stop: datetime) -> list:
        """
        Executes the module for an agent

        :param request_params: request params included
        :param auctions: list of auction to create bids
        :param start: start datetime
        :param stop: stop datetime
        :return: list of bids created.
        """
        print('in execute_user')
        return []

    def reset(self):
        """
        restart the module
        :return:
        """
        print('in reset')


const char * auction::getModuleInfo(int i )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start getModuleInfo \n");
    # endif

    / *fprintf(stderr, "count : getModuleInfo(%d)\n", i); * /

    switch(i)
    {
        case
    auction::I_MODNAME:
    return "Two Auction Module";
    case
    auction::I_ID:
    return "TwoAuction";
    case
    auction::I_VERSION:
    return "0.1";
    case
    auction::I_CREATED:
    return "2015/12/01";
    case
    auction::I_MODIFIED:
    return "2015/12/01";
    case
    auction::I_BRIEF:
    return "Auction process for spliting in low and high budget users";
    case
    auction::I_VERBOSE:
    return "The auction calculates a probability q, so high budget users are priced as low budget users.";
    case
    auction::I_HTMLDOCS:
    return "http://www.uniandes.edu.co/... ";
    case
    auction::I_PARAMS:
    return "None";
    case
    auction::I_RESULTS:
    return "The set of assigments";
    case
    auction::I_AUTHOR:
    return "Andres Marentes";
    case
    auction::I_AFFILI:
    return "Universidad de los Andes, Colombia";
    case
    auction::I_EMAIL:
    return "la.marentes455@uniandes.edu.co";
    case
    auction::I_HOMEPAGE:
    return "http://homepage";
    default:
    return NULL;
    }

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end getModuleInfo \n");
    # endif
}

char * auction::getErrorMsg(int code )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start getErrorMsg \n");
    # endif

    return NULL;

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end getErrorMsg \n");
    # endif
}
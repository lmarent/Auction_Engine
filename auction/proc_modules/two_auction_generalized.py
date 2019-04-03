
# Variables given as parameters.
uint32_t lastId;
ipap_field_container g_ipap_fields;
/*! auction = 0 if the auction corresponds to low budget
 * 			= 1 if the auction corresponds to high budget
*/

float
getResourceAvailability(auction::configParam_t *p arams, int auction )
{

    # ifdef DEBUG
    cout << "Starting getResourceAvailability - auction type:" << auction << endl;
    # endif

    # Check the parameter auction type.
    if ((auction < 0) || (auction > 1)){
        throw auction::ProcError(AUM_PROC_PARAMETER_ERROR,
                   "two auction generalized init module - auction type requested is wrong");
    }

    float bandwidth = 0;
    int numparams = 0;

    while (params[0].name != NULL) {

        # in all the application we establish the rates and
        # burst parameters in bytes
        if (auction == 0){
            cout << "in auction param name:" << params[0].name << endl;
            if (!strcmp(params[0].name, "bandwidth01")) {
                bandwidth = (float) parseFloat( params[0].value );
                numparams++;
            }
        }
        else {
            if (!strcmp(params[0].name, "bandwidth02")) {
                bandwidth = (float) parseFloat( params[0].value );
                numparams++;
            }
        }
        params++;
    }

    if (numparams == 0)
        throw
        auction::ProcError(AUM_PROC_PARAMETER_ERROR,
                           "two auction generalized init module - not enought parameters");

    if (bandwidth <= 0)
        throw
        auction::ProcError(AUM_PROC_BANDWIDTH_AVAILABLE_ERROR,
                           "two auction generalized init module - The given bandwidth parameter is incorrect");

    # ifdef DEBUG
    cout << "Ending getResourceAvailability - Bandwidth:" << bandwidth << endl;
    # endif

    return bandwidth;

}


double
getReservePrice(auction::configParam_t *p arams, int auction )
{
    double price = 0;
    int numparams = 0;

    # ifdef DEBUG
    cout << "Starting getReservePrice - auction:" << auction << endl;
    # endif

    # Check the parameter auction.
    if ((auction < 0) || (auction > 1)){
        throw auction::P
            rocError(AUM_PROC_PARAMETER_ERROR,
                      "two auction generalized init module - auction requested is wrong");
    }

    while (params[0].name != NULL) {
        # in all the application we establish the rates and  burst parameters in bytes
        if (auction == 0){
            if (!strcmp(params[0].name, "reserveprice01")) {
                price = (double) parseDouble( params[0].value );
                numparams++;
            }
        }
        else {
            if (!strcmp(params[0].name, "reserveprice02")) {
                price = (double) parseDouble( params[0].value );
                numparams++;
            }
        }
        params++;
    }

    if (numparams == 0)
        throw
        auction::ProcError(AUM_PROC_PARAMETER_ERROR,
                           "two auction init module - not enought parameters");

    if (price < 0)
        throw
        auction::ProcError(AUM_PRICE_RESERVE_ERROR,
                           "two auction init module - The given reserve price is incorrect");

    # ifdef DEBUG
    cout << "Ending getReservePrice" << price << endl;
    # endif

    return price;

}

double getMaximumValue(auction::configParam_t *p arams, int auction )
{
    double maximumValue = 0;
    int numparams = 0;

    # ifdef DEBUG
    cout << "Starting getMaximumValue - auction:" << auction << endl;
    # endif

    # Check the auction parameter
    if ((auction < 0) || (auction > 1)){
        throw auction::P
            rocError(AUM_PROC_PARAMETER_ERROR,
                      "two auction generalized init module - auction requested is wrong");
    }

    while (params[0].name != NULL) {
        # in all the application we establish the rates and burst parameters in bytes
        if (auction == 0){
            if (!strcmp(params[0].name, "maxvalue01")) {
                maximumValue = (double) parseDouble( params[0].value );
                numparams++;
            }
        }
        else {
            if (!strcmp(params[0].name, "maxvalue02")) {
                maximumValue = (double) parseDouble( params[0].value );
                numparams++;
            }
        }
        params++;
    }

    if (numparams == 0)
        throw
        auction::ProcError(AUM_PROC_PARAMETER_ERROR,
                           "two auction generalized init module - not enought parameters");

    if (maximumValue < 0)
        throw
        auction::ProcError(AUM_PRICE_RESERVE_ERROR,
                           "two auction generalized init module - The given reserve price is incorrect");

        # ifdef DEBUG
    cout << "Ending getMaximumValue" << maximumValue << endl;
    # endif

    return maximumValue;

}

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


void
auction::initModule(auction::configParam_t *p arams )
{

    cout << "two auction generalized module: start init module" << endl;

    # Bring fields defined for ipap_messages;
    g_ipap_fields.initialize_forward();
    g_ipap_fields.initialize_reverse();

    cout << "two auction generalized module: end init module" << endl;

}

void
auction::destroyModule(auction::configParam_t *p arams )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start destroy module \n");
    # endif


    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end destroy module \n");
    # endif

}


string makeKey(string auctionSet, string auctionName, string bidSet, string bidName)
{
    return auctionSet + "|" + auctionName + "|" + bidSet + "|" + bidName;
}

string getBidName(string allocationKey)
{
    cout << "start getBidName" << endl;

    std::size_t found = allocationKey.find_last_of("|");
    string bidName = allocationKey.substr(found+ 1 );

    cout << "ending getBidName:" << bidName << endl;
    return bidName;
}

auction::BiddingObject * createAllocation(auction::fieldDefList_t *f ieldDefs,
                                          auction::fieldValList_t *f ieldVals,
                                          string auctionSet, string auctionName, \
                                          string bidSet, string bidName, string sessionId,
                                          time_t start, time_t stop, float quantity, double price )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start create allocation \n");
    # endif

    uint64_t timeUint64;

    auction::elementList_t elements;
    auction::optionList_t options;

    auction::fieldList_t elementFields;
    string elementName = "key_1";

    # The set for the allocation is the same as the initial bid.
    string allocset = bidSet;

    # Create the id given.
    uint32_t lid = getId();
    string allocname = uint32ToString(lid);
    cout << "before calling refidobject" << endl;

    # Insert reference bidding object
    ipap_field fRef = g_ipap_fields.get_field(0, IPAP_FT_REFIDBIDDINGOBJECT);

    fillField(fieldDefs, fieldVals, 0, IPAP_FT_REFIDBIDDINGOBJECT, bidName, &e lementFields);

    # Insert quantity ipap_field
    fQuantity = g_ipap_fields.get_field(0, IPAP_FT_QUANTITY);
    ipap_value_field fVQuantity = fQuantity.get_ipap_value_field(quantity );
    string squantity = fQuantity.writeValue(fVQuantity);
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_QUANTITY, squantity, & elementFields);

    # ifdef DEBUG
    cout << "two auction generalized module: start create allocation after quantity" << std::endl;
    # endif

    # Insert Unit Value
    ipap_field fvalue = g_ipap_fields.get_field(0, IPAP_FT_UNITVALUE);
    ipap_value_field fVValue = fvalue.get_ipap_value_field(price);
    string svalue = fvalue.writeValue(fVValue);
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_UNITVALUE, svalue, & elementFields);

    # ifdef DEBUG
    cout << "two auction generalized module: start create allocation after unitvalue " << std::endl;
    # endif

    string recordId = "Unique";
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_IDRECORD, recordId, & elementFields);

    elements[elementName] = elementFields;

    # construct the interval with the allocation, based on start datetime and interval for the requesting auction

    auction::fieldList_t optionFields;

    # Insert start ipap_field
    fStart = g_ipap_fields.get_field(0, IPAP_FT_STARTSECONDS);
    timeUint64 = *reinterpret_cast < uint64_t * > (& start);
    ipap_value_field fVStart = fStart.get_ipap_value_field(timeUint64);
    string sstart = fStart.writeValue(fVStart);
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_STARTSECONDS, sstart, & optionFields);

    # ifdef DEBUG
    cout << "two auction generalized module: start create allocation after startSeconds" << std::endl;
    # endif

    # Insert stop ipap_field
    fStop = g_ipap_fields.get_field(0, IPAP_FT_ENDSECONDS);
    timeUint64 = *reinterpret_cast < uint64_t * > (& stop);
    ipap_value_field fVStop = fStop.get_ipap_value_field(timeUint64);
    string sstop = fStop.writeValue(fVStop);
    fillField(fieldDefs, fieldVals, 0, IPAP_FT_ENDSECONDS, sstop, & optionFields);

    # ifdef DEBUG
    cout << "two auction generalized module: start create allocation after endSeconds" << std::endl;
    # endif

    fillField(fieldDefs, fieldVals, 0, IPAP_FT_IDRECORD, recordId, & optionFields);
    options.push_back(pair < string, auction::fieldList_t > (elementName, optionFields));

    auction::BiddingObject * alloc = new
    auction::BiddingObject(auctionSet, auctionName,
                           allocset, allocname, IPAP_ALLOCATION, elements, options);

    # All objects must be inherit the session from the bid.
    alloc->setSession(sessionId);

    # ifdef DEBUG
    cout << "two auction generalized module: ending create allocation" << std::endl;
    # endif

    return alloc;
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

void
separateBids(auction::auctioningObjectDB_t * bids, double bl, double bh, auction::auctioningObjectDB_t * bids_low,
             auction::auctioningObjectDB_t * bids_high)
{

    # ifdef DEBUG
    cout << "Starting separateBids" << endl;
    # endif

    auction::auctioningObjectDB_t::iterator iter;
    for (iter = bids->begin();iter != bids->end(); ++iter){
        auction::BiddingObject * bid = dynamic_cast < auction::BiddingObject * > (*iter);

        double price = getBidPrice(bid);

        if (price >= 0)
        {
            if (price > bl)
            {
                bids_high->push_back(bid);
            }
            else {
                bids_low->push_back(bid);
            }
        }
    }

    # ifdef DEBUG
    cout << "Ending separateBids" << endl;
    # endif

}


void changeAllocationPrice(auction::fieldValList_t * fieldVals, auction::BiddingObject * allocation, double price)
{

    # ifdef DEBUG
    cout << "two auction generalized module: starting changeAllocationPrice" << endl;
    # endif

    auction::elementList_t * elements = allocation->getElements();

    # there is only one element.
    auction::fieldListIter_t field_iter;
    auction::field_t field;
    for (field_iter = (elements->begin()->second).begin();
        field_iter != (elements->begin()->second).end(); ++field_iter )
    {
        if ((field_iter->name).compare("unitprice") == 0)
        {
            # Delete the field. \
                field = *field_iter;
            string fvalue = doubleToString(price);
            field_iter->value[0] = auction::FieldValue(field_iter->type, fvalue);
            break;
        }
    }
    if (field.name.empty()){
        throw auction::
            ProcError("Field quantity was not included in the allocation");
    }

    # ifdef DEBUG
    cout << "two auction generalized module: ending changeAllocationPrice" << endl;
    # endif


}

void addQuantityAllocation(auction::fieldValList_t * fieldVals, auction::BiddingObject * allocation, float quantity)
{

    # ifdef DEBUG
    cout << "two auction generalized module: starting add quantity allocation" << endl;
    # endif

    auction::elementList_t * elements = allocation->getElements();

    # there is only one element.
    auction::fieldListIter_t field_iter;
    auction::field_t field;
    for (field_iter = (elements->begin()->second).begin(); field_iter != (elements->begin()->second).end(); ++field_iter )
    {
        if ((field_iter->name).compare("quantity") == 0)
        {
            # Delete the field.
            field = *field_iter;
            float temp_qty = parseFloat(((field.value)[0]).getValue());
            temp_qty += quantity;
            string fvalue = floatToString(temp_qty);
            field_iter->value[0] = auction::FieldValue(field_iter->type, fvalue);
            break;
        }
    }

    if (field.name.empty()){
        throw auction::
            ProcError("Field quantity was not included in the allocation");
    }

    # ifdef DEBUG
    cout << "two auction generalized module: ending add quantity allocation" << endl;
    # endif

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

void executeAuctionRandomAllocation(auction::fieldDefList_t * fieldDefs,
                                    auction::fieldValList_t * fieldVals,
                                    double price, string aset, string aname,
                                    time_t start, time_t stop, LAuctionRequestDB_t & bidsToFulfil,
                                    double qtyAvailable, map < string, auction::BiddingObject * > & allocations)
{

    # ifdef DEBUG
    cout << "execute Action random allocation" << endl;
    # endif

    double prob;
    map < string, auction::BiddingObject * >::iterator alloc_iter;

    int index;

    # Create allocations for Bids that are below the reserved price.
    for (int m = bidsToFulfil.size() - 1; m >= 0; m--){

        cout << "execute Action random allocation 1" << endl;

        for (int l = (bidsToFulfil[m]).size()-1; l >= 0; l--){

            cout << "execute Action random allocation m:" << m << "l:" << l << endl;

            if ((bidsToFulfil[m][l]).originalPrice < price){
                if ( allocations.find(makeKey(aset, aname, (bidsToFulfil[m][l]).bidSet, (bidsToFulfil[m][l]).bidName )) == allocations.end()) {
                    auction::BiddingObject * alloc = \
                    createAllocation(fieldDefs, fieldVals, aset, aname, (bidsToFulfil[m][l]).bidSet,
                             (bidsToFulfil[m][l]).bidName, (bidsToFulfil[m][l]).sessionId,
                             start, stop, 0, price);

                allocations[makeKey(aset, aname,
                        (bidsToFulfil[m][l]).bidSet, (bidsToFulfil[m][l]).bidName)] = alloc;
                }

                cout << "execute Action random allocation 2 - item:" << l << " original price:" << (
                    bidsToFulfil[m][l]).originalPrice << endl;

                # Remove the node.
                bidsToFulfil[m].erase((bidsToFulfil[m]).begin() + l);
            }
        }

        cout << "execute Action random allocation 2" << endl;
        # Remove the bid if all their price elements were less than the reserved price.
        if ((bidsToFulfil[m]).size() == 0)
        {
            bidsToFulfil.erase(bidsToFulfil.begin() + m);
        }

        cout << "execute Action random allocation 3" << endl;
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

    # ifdef DEBUG
    cout << "execute Action random allocation" << endl;
    # endif

}

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


void
ApplyMechanism(auction::fieldDefList_t * fieldDefs, auction::fieldValList_t * fieldVals,
                    time_t start, time_t stop, map < string, auction::BiddingObject * > & allocations,
                    double price, double Q)
{

    cout << "starting ApplyMechanism Q:" << Q << endl;

    map < string, auction::BiddingObject * >::iterator iter;
    for (iter = allocations.begin(); iter != allocations.end(); ++iter){

        string bidName = getBidName(iter->first);

        auction::BiddingObject * alloc = iter->second;
        int quantity = floor(getAllocationQuantity(fieldVals, alloc));
        float unitsToPass = 0;

        for (int j = 0; j < quantity; j++)
        {

            double prob = getProbability();

            if (prob <= Q) # pass a unit.
                unitsToPass = unitsToPass + 1;
        }

        cout << "bid set:" << alloc->getSet() << "qty to pass:" << unitsToPass << endl;

        if (unitsToPass > 0)
        {

            if (unitsToPass < quantity)
            {
                auction:: BiddingObject * alloc2 = createAllocation(fieldDefs, fieldVals,
                                                            alloc->getAuctionSet(), alloc->getAuctionName(),
                                                                                           alloc->getSet(), bidName,
                                                                                                  alloc->getSession(), start, stop, unitsToPass, price );

                float unitsToAdd = unitsToPass * -1;
                addQuantityAllocation(fieldVals, alloc, unitsToAdd);

                allocations[makeKey(alloc2->getAuctionSet(), alloc2->getAuctionName(),
                                                         alloc2->getSet(), alloc2->getName())] = alloc2;
            } else {
                changeAllocationPrice(fieldVals, alloc, price);
            }
        }
    }

    cout << "ending ApplyMechanism" << endl;
}

void auction::execute(auction::fieldDefList_t * fieldDefs, auction::fieldValList_t * fieldVals,
                      auction::configParam_t * params, string aset, string aname, time_t start, time_t stop,
                      auction::auctioningObjectDB_t * bids, auction::auctioningObjectDB_t ** allocationdata )
{

    # ifdef DEBUG
    cout << "two auction generalized module: start execute" << (int)
    bids->size() << endl;
    # endif

    float bandwidth_to_sell_low = getResourceAvailability(params, 0);
    float bandwidth_to_sell_high = getResourceAvailability(params, 1);
    double reserve_price_low = getReservePrice(params, 0);
    double reserve_price_high = getReservePrice(params, 1);
    double bl = getMaximumValue(params, 0);
    double bh = getMaximumValue(params, 1);

    float totalReq = calculateRequestedQuantities(bids);

    cout << "totalReq:" << totalReq << "total units:" << bandwidth_to_sell_low + bandwidth_to_sell_high << endl;

    if (totalReq > (bandwidth_to_sell_low + bandwidth_to_sell_high))
    {

        cout << "Splitting resources:" << endl;

        auction::auctioningObjectDB_t * bids_low = new
        auction::auctioningObjectDB_t();
        auction::auctioningObjectDB_t * bids_high = new
        auction::auctioningObjectDB_t();

        # Order bids classifying them by whether they compete on the low and high auction.
        separateBids(bids, bl, bh, bids_low, bids_high);

        # Calculate the number of bids on both auctions.
        int nl = calculateRequestedQuantities(bids_low);
        int nh = calculateRequestedQuantities(bids_high);

        double qStar = 0;
        double Q = 0.2;

        cout << "Starting the execution of the mechanism" << endl;

        if ((nl > 0) & & (nh > 0)){

            # Find the probability of changing from the high budget to low budget auction.
            TwoAuctionMechanismGeneralized * mechanism = new TwoAuctionMechanismGeneralized();
            double a = 0.01;
            double b = 0.8;

            mechanism->zeroin(nh, nl, bh, bl, bandwidth_to_sell_high,
                bandwidth_to_sell_low, reserve_price_high, reserve_price_low, Q, & a, & b);
            qStar = a;

            while ((qStar >= 0.25) and (Q <= 1.0))
            {
                Q = Q + 0.03;
                a = 0.01;
                b = 0.8;

                mechanism->zeroin(nh, nl, bh, bl, bandwidth_to_sell_high,
                              bandwidth_to_sell_low, reserve_price_high, reserve_price_low, Q, & a, & b);

                qStar = a;

                cout << "Q:" << Q << "qStar:" << qStar << endl;

            }

            delete mechanism;
        }

        cout << "Finished the execution of the mechanism" << endl;

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

        if (Q > 0)
        {
            # change bids from the high budget to low budget auction.
            ApplyMechanism(fieldDefs, fieldVals, start, stop, alloctions_high, reserve_price_low, Q);
        }

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
}

void
auction::execute_user(auction::fieldDefList_t * fieldDefs, auction::fieldValList_t * fieldVals,
                      auction::fieldList_t * requestparams, auction::auctioningObjectDB_t * auctions,
                      time_t start, time_t stop, auction::auctioningObjectDB_t ** biddata )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start execute_user \n");
    # endif
    # Nothing to do

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end execute_user \n");
    # endif

}

void
auction::destroy(auction::configParam_t * params )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start destroy \n");
    # endif

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end destroy \n");
    # endif
}

void
auction::reset(auction::configParam_t * params )
{
    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: start reset \n");
    # endif

    # ifdef DEBUG
    fprintf(stdout, "two auction generalized module: end reset \n");
    # endif
}

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
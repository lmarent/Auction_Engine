import unittest
from foundation.bidding_object_manager import BiddingObjectManager

# include <cppunit/TestCase.h>
# include <cppunit/extensions/HelperMacros.h>

# include "BiddingObject.h"
# include "FieldValue.h"
# include "FieldValParser.h"
# include "FieldDefParser.h"
# include "BiddingObjectFileParser.h"
# include "BiddingObjectManager.h"
# include "ModuleLoader.h"
# include "Module.h"
# include "ConstantsAum.h"
# include "ProcModule.h"


class SubsidyAuctionTest(unittest.TestCase):

    def setUp(self):
        try:

            string filename;
            auctioningObjectDB_t * new_bids = NULL;
            bids = new auctioningObjectDB_t();
            moduleName = "libsubsidyauction.so";

            BiddingObject * ptrBid, *ptrBid2;

            int domain = 1;
            string fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            string fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = BiddingObjectManager(domain)

            # Parse the bidding objects in file example_bids1.xml, it allocates the memory.
            filename = "../etc/example_generalized_bids1.xml"
            new_bids = manager.parse_bidding_objects(filename)
            self.assertEqual(len(new_bids) == 1)
            ptrBid = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            # Parse the bidding objects in file example_bids2.xml, it allocates the memory.
            domain = 2;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new
            BiddingObjectManager(domain, fieldname, fieldValuename, "");

            filename = "../etc/example_generalized_bids2.xml";
            new_bids = manager->parseBiddingObjects(filename);
            self.assertEqual(new_bids->size() == 1 );
            ptrBid2 = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            ptrBid = new BiddingObject(*ptrBid2);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            # Parse the bidding objects in file example_bids3.xml, it allocates the memory.
            domain = 3;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new BiddingObjectManager(domain, fieldname, fieldValuename, "");

            filename = "../etc/example_generalized_bids3.xml";
            new_bids = manager->parseBiddingObjects(filename);
            self.assertEqual(new_bids->size() == 1 );
            ptrBid2 = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            ptrBid = new BiddingObject(*ptrBid2);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            # Parse the bidding objects in file example_bids4.xml, it allocates the memory.
            domain = 4;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new BiddingObjectManager(domain, fieldname, fieldValuename, "");

            filename = "../etc/example_generalized_bids4.xml";
            new_bids = manager->parseBiddingObjects(filename);
            self.assertEqual(new_bids->size() == 1 );
            ptrBid2 = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            ptrBid = new BiddingObject(*ptrBid2);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            # Parse the bidding objects in file example_bids5.xml, it allocates the memory.
            domain = 5;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new BiddingObjectManager(domain, fieldname, fieldValuename, "");

            filename = "../etc/example_generalized_bids5.xml";
            new_bids = manager->parseBiddingObjects(filename);
            self.assertEqual(new_bids->size() == 1 );
            ptrBid2 = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            ptrBid = new BiddingObject(*ptrBid2);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            # Parse the bidding objects in file example_bids6.xml, it allocates the memory.
            domain = 6;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new BiddingObjectManager(domain, fieldname, fieldValuename, "");

            filename = "../etc/example_generalized_bids6.xml";
            new_bids = manager->parseBiddingObjects(filename);
            self.assertEqual(new_bids->size() == 1 );
            ptrBid2 = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            ptrBid = new BiddingObject(*ptrBid2);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            # Parse the bidding objects in file example_bids7.xml, it allocates the memory.
            domain = 7;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new BiddingObjectManager(domain, fieldname, fieldValuename, "");

            filename = "../etc/example_generalized_bids7.xml";
            new_bids = manager->parseBiddingObjects(filename);
            self.assertEqual(new_bids->size() == 1 );
            ptrBid2 = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            ptrBid = new BiddingObject(*ptrBid2);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            # Parse the bidding objects in file example_bids8.xml, it allocates the memory.
            domain = 8;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new BiddingObjectManager(domain, fieldname, fieldValuename, "");

            filename = "../etc/example_generalized_bids8.xml";
            new_bids = manager->parseBiddingObjects(filename);
            self.assertEqual(new_bids->size() == 1 );
            ptrBid2 = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            ptrBid = new BiddingObject(*ptrBid2);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            # Parse the bidding objects in file example_bids9.xml, it allocates the memory.
            domain = 9;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new BiddingObjectManager(domain, fieldname, fieldValuename, "");

            filename = "../etc/example_generalized_bids9.xml";
            new_bids = manager->parseBiddingObjects(filename);
            self.assertEqual(new_bids->size() == 1 );
            ptrBid2 = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            ptrBid = new BiddingObject(*ptrBid2);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            // Parse the bidding objects in file example_bids10.xml, it allocates the memory.
            domain = 10;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new BiddingObjectManager(domain, fieldname, fieldValuename, "");

            filename = "../etc/example_generalized_bids10.xml";
            new_bids = manager->parseBiddingObjects(filename);
            self.assertEqual(new_bids->size() == 1 );
            ptrBid2 = dynamic_cast < BiddingObject * > ((*new_bids)[0]);
            ptrBid = new BiddingObject(*ptrBid2);
            bids->push_back(ptrBid);
            saveDelete(new_bids);
            saveDelete(manager);

            # Load the configuration
            string configFileName = DEF_SYSCONFDIR "/auctionmanager/netaum.conf.xml";

            conf = new ConfigManager(AUM_CONFIGFILE_DTD, configFileName, "");

            # Load the module
            string libname, path, ext;

            string moduleDir = DEF_LIBDIR;
            loader = new ModuleLoader(conf, moduleDir.c_str() # module(lib) basedir
                                      moduleName, # modlist
                                      "Proc", # channel name prefix
                                      "AUM_PROCESSOR",  # Configuration group
                                      );

            # Finally, we create the bidding object manager required to execute the auction.
            domain = 11;
            fieldname = DEF_SYSCONFDIR "/auctionmanager/fielddef.xml";
            fieldValuename = DEF_SYSCONFDIR "/auctionmanager/fieldval.xml";
            manager = new BiddingObjectManager(domain, fieldname, fieldValuename, "");

        }
        catch(Error & e)
        {
            std:: cout << "Error:" << e.getError() << std::endl << std::flush;

        if (loader) {
            saveDelete(loader);
        }
            throw e;
        }

void
subsidyauction_Test::tearDown()
{
    if (loader != NULL){
        saveDelete(loader);
    }

    if (manager != NULL){
        saveDelete(manager);
    }

    if (conf != NULL){
        saveDelete(conf);
    }

    if (bids != NULL){
        saveDelete(bids);
    }
}


void
subsidyauction_Test::test_not_enough_quantities()
{
    auctioningObjectDB_t allocations;
    auctioningObjectDB_t * ptr = & allocations;
    string auctionSet = "1";
    string auctionName = "1";
    time_t start = time(NULL);
    time_t stop = start + 100;
    string paramName;
    string paramValue;

    mod = loader->getModule(moduleName.c_str());
    procmod = dynamic_cast < ProcModule * > (mod);

    if (procmod != NULL){

        # The following are the required parameters

        configParam_t * params = new configParam_t[5];
        int i = 0;

        string paramName1 = "bandwidth";
        string paramValue1 = "40";
        params[i].name = (char * ) paramName1.c_str();
        params[i].value = (char * ) paramValue1.c_str();
        i++;

        string paramName2 = "subsidy";
        string paramValue2 = "1.2";
        params[i].name = (char * ) paramName2.c_str();
        params[i].value = (char * ) paramValue2.c_str();
        i++;

        # Discriminating bid.
        string paramName3 = "maxvalue01";
        string paramValue3 = "0.5";
        params[i].name = (char * ) paramName3.c_str();
        params[i].value = (char * ) paramValue3.c_str();
        i++;

        string paramName4 = "reserveprice";
        string paramValue4 = "0.15";
        params[i].name = (char * ) paramName4.c_str();
        params[i].value = (char * ) paramValue4.c_str();
        i++;

        params[i].name = NULL;
        params[i].value = NULL;

        procmod->getAPI()->execute(manager->getFieldDefs(), manager->getFieldVals(), params,
            auctionSet, auctionName, start, stop, bids, & ptr );

        auctioningObjectDBIter_t iter;
        for (iter = ptr->begin(); iter != ptr->end(); iter++){
            cout << "info:" << ( * iter)->getInfo() << endl;
        }
    }
}


void
subsidyauction_Test::test_enough_quantities()
{
    auctioningObjectDB_t allocations;
    auctioningObjectDB_t * ptr = & allocations;
    string auctionSet = "1";
    string auctionName = "1";
    time_t start = time(NULL);
    time_t stop = start + 100;
    string paramName;
    string paramValue;

    mod = loader->getModule(moduleName.c_str());
    procmod = dynamic_cast < ProcModule * > (mod);

    if (procmod != NULL){

        # The following are the required parameters

        configParam_t * params = new configParam_t[5];
        int i = 0;

        string paramName1 = "bandwidth";
        string paramValue1 = "90";
        params[i].name = (char * ) paramName1.c_str();
        params[i].value = (char * ) paramValue1.c_str();
        i++;

        string paramName2 = "subsidy";
        string paramValue2 = "1.2";
        params[i].name = (char * ) paramName2.c_str();
        params[i].value = (char * ) paramValue2.c_str();
        i++;

        // Discriminating bid.
        string paramName3 = "maxvalue01";
        string paramValue3 = "0.5";
        params[i].name = (char * ) paramName3.c_str();
        params[i].value = (char * ) paramValue3.c_str();
        i++;

        string paramName4 = "reserveprice";
        string paramValue4 = "0.15";
        params[i].name = (char * ) paramName4.c_str();
        params[i].value = (char * ) paramValue4.c_str();
        i++;

        params[i].name = NULL;
        params[i].value = NULL;

        procmod->getAPI()->execute(manager->getFieldDefs(), manager->getFieldVals(), params, auctionSet, auctionName,
                                   start, stop, bids, & ptr );

        auctioningObjectDBIter_t iter;
        for (iter = ptr->begin(); iter != ptr->end(); iter++){
            cout << "info:" << ( * iter)->getInfo() << endl;
        }
    }
}
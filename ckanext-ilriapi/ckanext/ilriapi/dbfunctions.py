from .connection import getSession, closeSession
import json


def getConfidentialFields(dataset):
    dbSession = getSession()
    result = []
    try:
        cnfFields = dbSession.execute(
            "select dict_tblinfo.tbl_cod,dict_tblinfo.tbl_des,dict_clminfo.clm_cod,dict_clminfo.clm_des "
            "FROM " + dataset + ".dict_tblinfo," + dataset + ".dict_clminfo "
            "WHERE dict_tblinfo.tbl_cod = dict_clminfo.tbl_cod AND dict_clminfo.clm_protected = 1 ORDER BY dict_tblinfo.tbl_des,dict_clminfo.clm_des"
        )
        for field in cnfFields:
            result.append(
                {
                    "tblname": field[0],
                    "tbldesc": field[1],
                    "clmname": field[2],
                    "clmdesc": field[3],
                }
            )

    except Exception, e:
        print str(e)

    closeSession(dbSession)
    try:
        jsonData = json.dumps(result)
        return jsonData
    except:
        return "{}"

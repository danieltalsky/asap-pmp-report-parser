from collections import defaultdict
from string import Formatter

from app.asap import ASAP


class ASAPOutputFormat:
    """
    A flexible output format class that uses simple token replacement
    """

    PHI_FIELDS = [
        "PAT07",
        "PAT08",
        "PAT09",
        "PAT10",
        "PAT11",
        "PAT12",
        "PAT13",
        "PAT14",
        "PAT15",
        "PAT16",
        "PAT17",
    ]

    MISSING_FIELD_VALUE = "X"
    PHI_REPLACEMENT = "# REDACT #"

    output_template: str
    output_template_dispenses: str
    unsafe_phi_display: bool

    def __init__(self, unsafe_phi_display: bool = False):
        self.unsafe_phi_display = unsafe_phi_display

    def redact_phi_from_output_dict(self, output_dict: dict):
        """
        Redact fields marked as Personal Health Information to prevent HIPAA violation

        @param output_dict:
        @return:
        """
        for field_code in self.PHI_FIELDS:
            output_dict[field_code] = self.PHI_REPLACEMENT
        return output_dict

    def output(self, asap: ASAP) -> str:
        """
        Output `output_template` and `output_template_dispenses` with values from an ASAP report

        @param asap:
        @return:
        """
        asap_dict = defaultdict(lambda: self.MISSING_FIELD_VALUE)

        # generate the main dict
        for section in asap.sections:
            asap_dict = asap_dict | section.asdict()

        # add patient info
        patients = ""
        for patient in asap.patients:
            patient_dict = defaultdict(lambda: self.MISSING_FIELD_VALUE)
            for section in patient.sections:
                patient_dict = patient_dict | section.asdict()

            redacted_patient_dict = patient_dict if self.unsafe_phi_display else self.redact_phi_from_output_dict(
                patient_dict)

            patients += Formatter().vformat(
                self.output_template_dispenses, (), redacted_patient_dict
            )

        asap_dict["patients"] = patients

        output = Formatter().vformat(self.output_template, (), asap_dict)

        return output


class ASAPHTMLOutput(ASAPOutputFormat):
    output_template: str = """<!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>ASAP Report</title>
          <meta name="description" content="ASAP HTML Output generated by ">
          <style>
          body {{ font-family: sans-serif; }}
          th {{ padding: 2px; }}
          th>div {{ font-size: .4em; }}
          td {{ padding: 4px; font-size: 1.4em; font-family: monospace;}}
          section.dispenses {{ margin: 1em; background: #eee; padding: 1em;}}
          section.dispense {{ margin: 1em; padding: 1em; background: #e6eeff; }}
          </style>
        </head>
        
        <body>
            <h1>ASAP {TH01} Report Output for {IS02}</h1>
            
            <section class="th">
            <h2>TH (Transaction Header)</h2>
            <table border="1">
                <tr>
                    <th>TH01<div>Version</div></th>
                    <th>TH02<div>Transaction Control Number</div></th>
                    <th>TH03</th>
                    <th>TH04</th>
                    <th>TH05<div>Creation Date</div></th>
                    <th>TH06<div>Creation Time</div></th>
                    <th>TH07</th>
                    <th>TH08</th>
                    <th>TH09</th>
                </tr>
                <tr>
                    <td>{TH01}</td>
                    <td>{TH02}</td>
                    <td>{TH03}</td>
                    <td>{TH04}</td>
                    <td>{TH05}</td>
                    <td>{TH06}</td>
                    <td>{TH07}</td>
                    <td>{TH08}</td>
                    <td>{TH09}</td>
                </tr>                
            </table>
            </section>

            <section class="is">
            <h2>IS (Information Source)</h2>
            <table border="1">
                <tr>
                    <th>IS01<div>Source ID</div></th>
                    <th>IS02<div>Source Name</div></th>
                    <th>IS03</th>
                </tr>
                <tr>
                    <td>{IS01}</td>
                    <td>{IS02}</td>
                    <td>{IS03}</td>
                </tr>                
            </table>
            </section>            
        
            <section class="pha">
            <h2>PHA (Pharmacy Header)</h2>
            <table border="1">
                <tr>
                    <th>PHA01<div>NPI</div></th>
                    <th>PHA02</th>
                    <th>PHA03<div>DEA Number</div></th>
                    <th>PHA04</th>
                    <th>PHA05</th>
                    <th>PHA06</th>
                    <th>PHA07</th>
                    <th>PHA08</th>
                    <th>PHA09</th>
                    <th>PHA10</th>
                    <th>PHA11</th>
                    <th>PHA12</th>
                    <th>PHA13</th>
                </tr>
                <tr>
                    <td>{PHA01}</td>
                    <td>{PHA02}</td>
                    <td>{PHA03}</td>
                    <td>{PHA04}</td>
                    <td>{PHA05}</td>
                    <td>{PHA06}</td>
                    <td>{PHA07}</td>
                    <td>{PHA08}</td>
                    <td>{PHA09}</td>
                    <td>{PHA10}</td>
                    <td>{PHA11}</td>
                    <td>{PHA12}</td>
                    <td>{PHA13}</td>
                </tr>                
            </table>
            </section>        
            
            <section class="dispenses">
            <h2>Patients</h2>
            {patients}
            </section>
            
            <section class="tp">
            <h2>TP (Pharmacy Trailer)</h2>
            <table border="1">
                <tr>
                    <th>TP01<div>Detail Segment Count</div></th>
                </tr>
                <tr>
                    <td>{TP01}</td>
                </tr>                
            </table>
            </section>     
            
            <section class="tt">
            <h2>TT (Transaction Trailer)</h2>
            <table border="1">
                <tr>
                    <th>TT01<div>Transaction Control Number</div></th>
                    <th>TT02<div>Segment Count</div></th>
                </tr>
                <tr>
                    <td>{TT01}</td>
                    <td>{TT02}</td>
                </tr>                
            </table>
            </section>                             
            
        </body>
        </html>
    """

    output_template_dispenses = """
            <section class="dispense">
            <h3>A Set of Patient Records:</h3>
        
                <section class="pat">
                <h2>PAT (Patient Information)</h2>
                <table border="1">
                    <tr>
                        <th>PAT01</th>
                        <th>PAT02</th>
                        <th>PAT03<div>Patient ID</div></th>
                        <th>PAT04</th>
                        <th>PAT05</th>
                        <th>PAT06</th>
                        <th>PAT07<div>Last Name</div></th>
                        <th>PAT08<div>First Name</div></th>
                        <th>PAT09<div>Middle Name</div></th>
                        <th>PAT10</th>
                        <th>PAT11</th>
                        <th>PAT12<div>Address 1</div></th>
                        <th>PAT13<div>Address 2</div></th>
                        <th>PAT14<div>City</div></th>
                        <th>PAT15<div>State</div></th>
                        <th>PAT16<div>ZIP</div></th>
                        <th>PAT17<div>Phone</div></th>
                        <th>PAT18<div>D.O.B.</div></th>
                        <th>PAT19<div>Sex</div></th>
                        <th>PAT20</th>
                        <th>PAT21</th>
                        <th>PAT22</th>
                        <th>PAT23</th>                
                    </tr>
                    <tr>
                        <td>{PAT01}</td>
                        <td>{PAT02}</td>
                        <td>{PAT03}</td>
                        <td>{PAT04}</td>
                        <td>{PAT05}</td>
                        <td>{PAT06}</td>
                        <td>{PAT07}</td>
                        <td>{PAT08}</td>
                        <td>{PAT09}</td>
                        <td>{PAT10}</td>
                        <td>{PAT11}</td>
                        <td>{PAT12}</td>
                        <td>{PAT13}</td>
                        <td>{PAT14}</td>
                        <td>{PAT15}</td>
                        <td>{PAT16}</td>
                        <td>{PAT17}</td>
                        <td>{PAT18}</td>
                        <td>{PAT19}</td>
                        <td>{PAT20}</td>
                        <td>{PAT21}</td>
                        <td>{PAT22}</td>
                        <td>{PAT23}</td>
                    </tr>                
                </table>
                </section>     

                <section class="dsp">
                <h2>DSP (Dispensing Record)</h2>
                <table border="1">
                    <tr>
                        <th>DSP01</th>
                        <th>DSP02<div>Prescription Number</div></th>
                        <th>DSP03<div>Date Written</div></th>
                        <th>DSP04<div>Refills</div></th>
                        <th>DSP05<div>Date Filled</div></th>
                        <th>DSP06<div>Fill Number</div></th>
                        <th>DSP07<div>Qualifier</div></th>
                        <th>DSP08<div>Product ID</div></th>
                        <th>DSP09<div>Quantity</div></th>
                        <th>DSP10<div>Days Supply</div></th>
                        <th>DSP11<div>Unit Code</div></th>
                        <th>DSP12<div>Transmission</div></th>
                        <th>DSP13<div>Partial?</div></th>
                        <th>DSP14</th>
                        <th>DSP15</th>
                        <th>DSP16<div>Payment Type</div></th>
                        <th>DSP17</th>
                        <th>DSP18</th>
                        <th>DSP19</th>
                        <th>DSP20</th>
                        <th>DSP21</th>
                        <th>DSP22</th>
                        <th>DSP23</th>                
                        <th>DSP24</th>                
                        <th>DSP25</th>                
                    </tr>
                    <tr>
                        <td>{DSP01}</td>
                        <td>{DSP02}</td>
                        <td>{DSP03}</td>
                        <td>{DSP04}</td>
                        <td>{DSP05}</td>
                        <td>{DSP06}</td>
                        <td>{DSP07}</td>
                        <td>{DSP08}</td>
                        <td>{DSP09}</td>
                        <td>{DSP10}</td>
                        <td>{DSP11}</td>
                        <td>{DSP12}</td>
                        <td>{DSP13}</td>
                        <td>{DSP14}</td>
                        <td>{DSP15}</td>
                        <td>{DSP16}</td>
                        <td>{DSP17}</td>
                        <td>{DSP18}</td>
                        <td>{DSP19}</td>
                        <td>{DSP20}</td>
                        <td>{DSP21}</td>
                        <td>{DSP22}</td>
                        <td>{DSP23}</td>
                        <td>{DSP24}</td>
                        <td>{DSP25}</td>
                    </tr>                
                </table>
                </section>     

                <section class="pre">
                <h2>PRE (Prescriber Information)</h2>
                <table border="1">
                    <tr>
                        <th>PRE01<div>NPI</div></th>
                        <th>PRE02<div>DEA Number</div></th>
                        <th>PRE03</th>
                        <th>PRE04</th>
                        <th>PRE05</th>
                        <th>PRE06</th>
                        <th>PRE07</th>
                        <th>PRE08</th>
                        <th>PRE09</th>
                        <th>PRE10</th>             
                    </tr>
                    <tr>
                        <td>{PRE01}</td>
                        <td>{PRE02}</td>
                        <td>{PRE03}</td>
                        <td>{PRE04}</td>
                        <td>{PRE05}</td>
                        <td>{PRE06}</td>
                        <td>{PRE07}</td>
                        <td>{PRE08}</td>
                        <td>{PRE09}</td>
                        <td>{PRE10}</td>
                    </tr>                
                </table>
                </section>     
            
                <section class="pre">
                <h2>AIR (Additional Information Reporting)</h2>
                <table border="1">
                    <tr>
                        <th>AIR01<div>State Issuing Rx ID</div></th>
                        <th>AIR02<div>State Rx ID</div></th>
                        <th>AIR03<div>ID Jurisdiction</div></th>
                        <th>AIR04</th>
                        <th>AIR05</th>
                        <th>AIR06</th>
                        <th>AIR07<div>Dropoff Last Name</div></th>
                        <th>AIR08<div>Dropoff First Name</div></th>
                        <th>AIR09<div>Pharmacist Last Name</div></th>
                        <th>AIR10<div>Pharmacist First Name</div></th>             
                        <th>AIR11</th>             
                    </tr>
                    <tr>
                        <td>{AIR01}</td>
                        <td>{AIR02}</td>
                        <td>{AIR03}</td>
                        <td>{AIR04}</td>
                        <td>{AIR05}</td>
                        <td>{AIR06}</td>
                        <td>{AIR07}</td>
                        <td>{AIR08}</td>
                        <td>{AIR09}</td>
                        <td>{AIR10}</td>
                        <td>{AIR11}</td>
                    </tr>                
                </table>
                </section>                 
            
            </section>  
    """

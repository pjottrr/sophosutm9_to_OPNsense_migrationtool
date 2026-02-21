import time
from pysense.api.acmeclient_accounts_client import AcmeclientAccountsClient
from pysense.api.acmeclient_certificates_client import AcmeclientCertificatesClient
from pysense.api.acmeclient_validations_client import AcmeclientValidationsClient
from pysense.pydantic.Certificate import Certificate
from pysense.pydantic.SearchRequest import SearchRequest


class Acmeclient(AcmeclientCertificatesClient, AcmeclientAccountsClient, AcmeclientValidationsClient):

    def acmecient(self, domain, account_value, renew_interval=15) -> Certificate:
        certificates = self.acmeclient_certificates_search(SearchRequest.search(domain))
        for certificate in certificates.rows: # type: Certificate
            if certificate.name == domain:
                print("Warning certificate already exists")
                return certificate
        accounts = self.acmeclient_accounts_search()
        account_uuid = None
        if len(accounts.rows) == 1:
            account_uuid = accounts.rows[0].uuid
        for account in accounts.rows:
            if account.name == account_value or account.uuid == account_value:
                account_uuid = account.uuid
        if account_uuid is None:
            raise Exception("Account not found")

        validations = self.acmeclient_validations_search()
        validations_uuid = None
        if len(validations.rows) == 1:
            validations_uuid = validations.rows[0].uuid
        if validations_uuid is None:
            raise Exception("Validation not found")

        item = Certificate(
            enabled=True,
            name=domain,
            account=str(account_uuid),
            validationMethod=str(validations_uuid),
            keyLength=Certificate.CertificatesCertificateKeylengthEnum.KEY_4096,
            ocsp=False,
            autoRenewal=True,
            renewInterval=renew_interval,
            aliasmode=Certificate.CertificatesCertificateAliasmodeEnum.NONE
        )
        cert = self.acmeclient_certificates_add(item)
        self.acmeclient_certificates_sign(cert.uuid)
        return self.acmeclient_certificates_get(cert.uuid)

    def acmeclient_wait_cert_issued(self, domain, timeout=10, interval_sleep=1) -> Certificate | None:
        """
        The certRefId will be set after the certificate is issued. This can take a undefined amount of time.
        (acme server rate limits for example). Only after the certificate is issued it can be connected to a service

        :param interval_sleep: time to sleep in between attempts
        :param timeout: time in seconds to wait for the certificate to be issued
        :param domain:
        :return: None on timeout else CertificateResponse
        """
        start = time.time()

        while time.time() - start < timeout:
            certificates = self.acmeclient_certificates_search(domain)
            for cert in certificates.rows:
                if cert.name == domain:
                    if cert.certRefId is not None:
                        return cert
            time.sleep(interval_sleep)
        else:
            print("Error: Unable to assign certificate due to certificate not issued in time")
            return None
        return certificate

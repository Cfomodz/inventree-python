# -*- coding: utf-8 -*-

import inventree.base
import inventree.report
import inventree.stock


class Build(
    inventree.base.AttachmentMixin,
    inventree.base.ParameterMixin,
    inventree.base.StatusMixin,
    inventree.base.MetadataMixin,
    inventree.report.ReportPrintingMixin,
    inventree.base.InventreeObject,
):
    """ Class representing the Build database model """

    URL = 'build/'
    MODEL_TYPE = 'build'

    def issue(self):
        """Mark this build as 'issued'."""
        return self._statusupdate(status='issue')

    def hold(self):
        """Mark this build as 'on hold'."""
        return self._statusupdate(status='hold')

    def complete(
        self,
        accept_overallocated='reject',
        accept_unallocated=False,
        accept_incomplete=False,
    ):
        """Finish a build order. Takes the following flags:
        - accept_overallocated
        - accept_unallocated
        - accept_incomplete
        """
        return self._statusupdate(
            status='finish',
            data={
                'accept_overallocated': accept_overallocated,
                'accept_unallocated': accept_unallocated,
                'accept_incomplete': accept_incomplete,
            }
        )

    def finish(self, *args, **kwargs):
        """Alias for complete"""
        return self.complete(*args, **kwargs)

    def getLines(self, **kwargs):
        """ Return the build line items associated with this build order """
        return BuildLine.list(self._api, build=self.pk, **kwargs)

    def getBuildOutputs(self, complete: bool = None, **kwargs):
        """ Return the build output items associated with this build order

        Arguments:
            - complete: If not None, filter the build outputs by their 'complete' status
        """
        if complete is not None:
            kwargs['complete'] = complete

        # Find stock items which are marked as 'outputs' of this build order
        return inventree.stock.StockItem.list(
            self._api,
            build=self.pk,
            **kwargs
        )

    def createBuildOutput(self, **kwargs):
        """ Create a new build output (stock item) associated with this build order """
        result = self._api.post(
            f'{self.URL}{self.pk}/create-output/',
            data={
                **kwargs
            }
        )

        # Note: The response is a list of created stock items
        return [inventree.stock.StockItem(self._api, item['pk'], item) for item in result]

    def cancelBuildOutputs(self, outputs):
        """ Cancel a build output item associated with this build order

        Arguments:
            - outputs: The StockItem object (or list of StockItem objects, or PK(s)) to cancel
        """

        if not isinstance(outputs, list):
            outputs = [outputs]

        for idx, output in outputs:
            if isinstance(output, inventree.stock.StockItem):
                outputs[idx] = output.pk

        return self._api.post(
            f'{self.URL}delete-outputs/',
            data={
                'outputs': outputs,
            }
        )

    def scrapBuildOutput(self, outputs, **kwargs):
        """ Scrap a build output item associated with this build order

        Arguments:
            - outputs: The StockItem object (or list of StockItem objects, or PK(s)) to scrap
        """
        if not isinstance(outputs, list):
            outputs = [outputs]

        for idx, output in outputs:
            if isinstance(output, inventree.stock.StockItem):
                outputs[idx] = output.pk

        return self._api.post(
            f'{self.URL}scrap-outputs/',
            data={
                'build': self.pk,
                'outputs': {
                    # TODO
                },
                **kwargs
            }
        )

    def completeBuildOutput(self, stock_item, **kwargs):
        """ Mark a build output item as complete

        Arguments:
            - stock_item: The StockItem object (or PK) to mark as complete
        """
        if isinstance(stock_item, inventree.stock.StockItem):
            stock_item = stock_item.pk

        return self._api.post(
            f'{self.URL}complete_output/',
            data={
                'build': self.pk,
                'stock_item': stock_item,
                **kwargs
            }
        )


class BuildLine(
    inventree.base.InventreeObject,
):
    """ Class representing the BuildLine database model """

    URL = 'build/line/'
    MODEL_TYPE = 'buildline'

    def getBuild(self):
        """Return the Build object associated with this line item"""
        return Build(self._api, self.build)


class BuildItem(
    inventree.base.InventreeObject,
):
    """ Class representing the BuildItem database model """

    URL = 'build/item/'
    MODEL_TYPE = 'builditem'

    def getBuild(self):
        """Return the Build object associated with this build item"""
        return Build(self._api, self.build)

    def getBuildLine(self):
        """Return the BuildLine object associated with this build item"""
        return BuildLine(self._api, self.build_line)

    def getStockItem(self):
        """Return the StockItem object associated with this build item"""
        return inventree.stock.StockItem(self._api, self.stock_item)

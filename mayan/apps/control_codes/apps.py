from __future__ import unicode_literals

from django.apps import apps
from django.db.models.signals import post_migrate, post_save
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.acls.links import link_acl_list
from mayan.apps.acls.permissions import permission_acl_edit, permission_acl_view
from mayan.apps.documents.signals import post_version_upload
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.html_widgets import TwoStateWidget
from mayan.apps.common.menus import (
    menu_facet, menu_list_facet, menu_object, menu_secondary, menu_setup
)
from mayan.apps.events.classes import ModelEventType
from mayan.apps.events.links import (
    link_events_for_object, link_object_event_types_user_subcriptions_list
)
from mayan.apps.navigation.classes import SourceColumn

from .control_codes import *
from .dependencies import *  # NOQA
from .handlers import (
    handler_create_control_sheet_codes_image_cache,
    handler_process_document_version
)
from .links import (
    link_control_sheet_create, link_control_sheet_delete,
    link_control_sheet_edit, link_control_sheet_list,
    link_control_sheet_preview,

    link_control_sheet_code_delete, link_control_sheet_code_edit,
    link_control_sheet_code_list
)
from .methods import method_document_submit, method_document_version_submit
from .permissions import (
    permission_control_sheet_delete, permission_control_sheet_edit,
    permission_control_sheet_view
)


class ControlCodesApp(MayanAppConfig):
    app_namespace = 'control_codes'
    app_url = 'control_codes'
    has_rest_api = True
    has_tests = False
    name = 'mayan.apps.control_codes'
    verbose_name = _('Control codes')

    def ready(self):
        super(ControlCodesApp, self).ready()
        from actstream import registry

        ControlSheet = self.get_model(model_name='ControlSheet')
        ControlSheetCode = self.get_model(model_name='ControlSheetCode')
        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )
        DocumentVersion = apps.get_model(
            app_label='documents', model_name='DocumentVersion'
        )

        Document.add_to_class(
            name='submit_for_control_codes_processing',
            value=method_document_submit
        )
        DocumentVersion.add_to_class(
            name='submit_for_control_codes_processing',
            value=method_document_version_submit
        )

        ModelPermission.register(
            model=ControlSheet, permissions=(
                permission_control_sheet_delete,
                permission_control_sheet_edit,
                permission_control_sheet_view
            )
        )

        ModelPermission.register_inheritance(
            model=ControlSheetCode, related='control_sheet',
        )

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=ControlSheet
        )

        SourceColumn(
            attribute='get_label', is_identifier=True,# is_sortable=True,
            source=ControlSheetCode
        )
        SourceColumn(
            attribute='order', is_sortable=True,
            source=ControlSheetCode
        )
        SourceColumn(
            attribute='arguments',
            source=ControlSheetCode
        )

        menu_list_facet.bind_links(
            links=(
                link_acl_list, #link_events_for_object,
                #link_object_event_types_user_subcriptions_list,
            ), sources=(ControlSheet,)
        )
        menu_list_facet.bind_links(
            links=(
                link_control_sheet_code_list,
            ),
            sources=(ControlSheet,)
        )
        menu_object.bind_links(
            links=(
                link_control_sheet_edit, link_control_sheet_delete,
                link_control_sheet_preview,
            ),
            sources=(ControlSheet,)
        )
        menu_object.bind_links(
            links=(
                link_control_sheet_code_delete, link_control_sheet_code_edit,
            ),
            sources=(ControlSheetCode,)
        )
        menu_secondary.bind_links(
            links=(link_control_sheet_list, link_control_sheet_create),
            sources=(
                ControlSheet, 'control_sheet:control_sheet_list',
                'control_sheet:control_sheet_create'
            )
        )
        menu_setup.bind_links(
            links=(link_control_sheet_list,),
        )

        post_migrate.connect(
            dispatch_uid='control_codes_handler_create_control_sheet_codes_image_cache',
            receiver=handler_create_control_sheet_codes_image_cache,
        )
        post_version_upload.connect(
            dispatch_uid='control_codes_handler_process_document_version',
            receiver=handler_process_document_version, sender=DocumentVersion
        )
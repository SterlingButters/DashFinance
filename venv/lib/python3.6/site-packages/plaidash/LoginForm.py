# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class LoginForm(Component):
    """A LoginForm component.
Description of LoginForm

Keyword arguments:
- id (string; optional): id
- apiVersion (string; optional): ApiVersion flag to use new version of Plaid API
- clientName (string; required): Displayed once a user has successfully linked their account
- env (a value equal to: 'tartan', 'sandbox', 'development', 'production'; required): The Plaid API environment on which to create user accounts.
For development and testing, use tartan. For production, use production
- institution (string; optional): Open link to a specific institution, for a more custom solution
- publicKey (string; required): The public_key associated with your account; available from
the Plaid dashboard (https://dashboard.plaid.com)
- product (list; required): The Plaid products you wish to use, an array containing some of connect,
auth, identity, income, transactions, assets
- token (string; optional): Specify an existing user's public token to launch Link in update mode.
This will cause Link to open directly to the authentication step for
that user's institution.
- public_token (string; optional): This is the token that will be returned for use in Dash. Can also be
understood as the "output" of this component
- selectAccount (boolean; optional): Set to true to launch Link with the 'Select Account' pane enabled.
Allows users to select an individual account once they've authenticated
- webhook (string; optional): Specify a webhook to associate with a user."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, apiVersion=Component.UNDEFINED, clientName=Component.REQUIRED, env=Component.REQUIRED, institution=Component.UNDEFINED, publicKey=Component.REQUIRED, product=Component.REQUIRED, token=Component.UNDEFINED, public_token=Component.UNDEFINED, selectAccount=Component.UNDEFINED, webhook=Component.UNDEFINED, onSuccess=Component.UNDEFINED, onExit=Component.UNDEFINED, onLoad=Component.UNDEFINED, onEvent=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'apiVersion', 'clientName', 'env', 'institution', 'publicKey', 'product', 'token', 'public_token', 'selectAccount', 'webhook']
        self._type = 'LoginForm'
        self._namespace = 'plaidash'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'apiVersion', 'clientName', 'env', 'institution', 'publicKey', 'product', 'token', 'public_token', 'selectAccount', 'webhook']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['clientName', 'env', 'publicKey', 'product']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(LoginForm, self).__init__(**args)

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('LoginForm(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'LoginForm(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')

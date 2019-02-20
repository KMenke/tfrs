import PropTypes from 'prop-types';
import React from 'react';
import { Link } from 'react-router-dom';

import { CREDIT_TRANSACTIONS_HISTORY, HISTORICAL_DATA_ENTRY, ROLES, USERS } from '../../constants/routes/Admin';
import PERMISSIONS_CREDIT_TRANSACTIONS from '../../constants/permissions/CreditTransactions';

const AdminTabs = props => (
  <ul className="admin-tabs nav nav-tabs" key="nav" role="tablist">
    {props.loggedInUser.hasPermission(PERMISSIONS_CREDIT_TRANSACTIONS.USE_HISTORICAL_DATA_ENTRY) &&
    <li role="presentation" className={`${(props.active === 'historical-data') ? 'active' : ''}`}>
      <Link id="navbar-administration" to={HISTORICAL_DATA_ENTRY.LIST}>
        Historical Data Entry
      </Link>
    </li>
    }
    {props.loggedInUser.isGovernmentUser && [
      <li
        role="presentation"
        key="user-activity"
        className={`${(props.active === 'user-activity') ? 'active' : ''}`}
      >
        <Link id="navbar-administration" to={CREDIT_TRANSACTIONS_HISTORY.LIST}>
          User Activity
        </Link>
      </li>,
      <li
        role="presentation"
        className={`${(props.active === 'users') ? 'active' : ''}`}
        key="user-list"
      >
        <Link id="navbar-administration" to={USERS.LIST}>
          Users
        </Link>
      </li>,
      <li
        role="presentation"
        className={`${(props.active === 'roles') ? 'active' : ''}`}
        key="roles"
      >
        <Link id="navbar-administration" to={ROLES.LIST}>
          Roles
        </Link>
      </li>
    ]}
  </ul>
);

AdminTabs.propTypes = {
  active: PropTypes.string.isRequired,
  loggedInUser: PropTypes.shape({
    hasPermission: PropTypes.func,
    isGovernmentUser: PropTypes.bool
  }).isRequired
};

export default AdminTabs;

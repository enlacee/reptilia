/* eslint-disable no-console */
import Vue from 'vue'
import Router from 'vue-router'
import Login from '@/components/Login/Login'
import Dashboard from '@/components/Dashboard/Dashboard'
import CreateList from '@/components/List/Form/FormList'
import List from '@/components/List/List/List'
import UserForm from '@/components/UserForm/UserForm'
import ChargeList from '@/components/Charge/List/Charge'
import ChargeForm from '@/components/Charge/Form/ChargeForm'
import DashboardLayout from '@/components/Layouts/dashboard/DashboardLayout'
import RemoteAgentsList from '@/components/RemoteAgents/List/RemoteAgentsList'
import CampaignList from '@/components/Campaign/List/CampaignList'

import axios from 'axios'
import { API_URL } from '../config'

Vue.use(Router)

const router = new Router({
    mode: 'history',
    routes: [
        {
            path: '/',
            name: 'Login',
            component: Login,
            meta: {
                title: 'Login'
            }
        },
        {
            path: '/dashboard',
            component: DashboardLayout,
            children: [
                {
                    path: '/dashboard',
                    name: 'Dashboard',
                    component: Dashboard,
                    meta: {
                        module: 'Dashboard',
                        title: 'Dashboard'
                    }
                },
                {
                    path: '/charge',
                    name: 'ChargeList',
                    component: ChargeList,
                    meta: {
                        module: 'ChargeList',
                        title: 'Cargas'
                    }
                },
                {
                    path: '/charge-form',
                    name: 'ChargeForm',
                    component: ChargeForm,
                    meta: {
                        module: 'ChargeList',
                        title: 'Subir lista'
                    }
                },
                {
                    path: '/lists',
                    name: 'List',
                    component: List,
                    meta: {
                        module: 'List',
                        title: 'Listas'
                    }
                },
                {
                    path: '/create-list',
                    name: 'ListForm',
                    component: CreateList,
                    meta: {
                        module: 'List',
                        title: 'Crear lista'
                    }
                },
                {
                    path: '/remote-agents-list',
                    name: 'RemoteAgentsList',
                    component: RemoteAgentsList,
                    meta: {
                        module: 'RemoteAgentsList',
                        title: 'Lista de agentes'
                    }
                },
                {
                    path: '/campaign-list',
                    name: 'CampaignList',
                    component: CampaignList,
                    meta: {
                        module: 'CampaignList',
                        title: 'Lista de campañas'
                    }
                },
                {
                    path: '/user-form',
                    name: 'UserForm',
                    component: UserForm,
                    meta: {
                        module: 'UserForm',
                        title: 'Formulario de usuario'
                    }
                }
            ]
        },
        {
            path: '*',
            redirect: '/'
        }
    ]
})

router.beforeEach((to, from, next) => {
    document.title = to.meta.title || 'Rept'

    let def = true

    if(to.name != 'Login'){
        def = '/'
    }

    axios.post(`${API_URL}/validate`, {
        name : to.name,
        module : to.meta.module,
    }, {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        }
    }).then((res) => {
        if(res.data.status){
            if(res.data.new_route){
                next({
                    name: res.data.route_name
                })
            }else{
                next()
            }
        }else {
            next({
                path: def
            })
        }
    }).catch((err) => {
        console.log(err)
        next({
            path: def
        })
    })
})

export default router
